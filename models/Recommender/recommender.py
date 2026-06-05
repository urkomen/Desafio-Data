"""
Lógica de recomendación: construcción del prompt enriquecido, vector de perfil
(historial positivo + favoritos), y scoring por similitud coseno sobre los
candidatos ya filtrados por los filtros duros.

Modelo: intfloat/multilingual-e5-large -> requiere prefijos 'query:' / 'passage:'.
"""
from datetime import datetime
import numpy as np

import config
import data_access as da
import location as loc


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _hoy():
    return datetime.today()


def calcular_alpha_beta(n_historial):
    """Peso consulta (α) vs perfil (β) según riqueza del historial."""
    if n_historial < 3:
        return 0.9, 0.1
    elif n_historial <= 10:
        return 0.7, 0.3
    return 0.5, 0.5


def calcular_penalizacion(fecha_str):
    """Penalización por lugar ya visitado; decae linealmente hasta 0 a los 90 días."""
    if not fecha_str:
        return 0.0
    try:
        fecha = datetime.strptime(fecha_str[:10], "%Y-%m-%d")
    except ValueError:
        return 0.0
    dias = (_hoy() - fecha).days
    if dias >= 90:
        return 0.0
    return round(0.3 * (1 - dias / 90), 4)


def describir_familia(familia):
    """Texto natural de la familia para el prompt."""
    edades = familia.get("edades", [])
    mascotas = familia.get("mascotas", [])
    partes = []
    if edades:
        menores = [e for e in edades if e < 18]
        adultos = [e for e in edades if e >= 18]
        if menores:
            partes.append(
                "niños de " + ", ".join(str(e) for e in menores) + " años"
            )
        if adultos:
            partes.append(f"{len(adultos)} adulto(s)")
    if mascotas:
        partes.append("con mascota")
    return "familia con " + ", ".join(partes) if partes else ""


# ──────────────────────────────────────────────────────────────
# PROMPT
# ──────────────────────────────────────────────────────────────

def construir_prompt(consulta, familia, historial, id_to_nombre):
    """
    Prompt enriquecido (prefijo 'query:' para e5):
    consulta del usuario + perfil familiar + historial ponderado por rating.
    """
    perfil = describir_familia(familia)

    encantados  = [id_to_nombre.get(h["event_id"]) for h in historial if h["rating"] == 5]
    gustados    = [id_to_nombre.get(h["event_id"]) for h in historial if h["rating"] == 4]
    regulares   = [id_to_nombre.get(h["event_id"]) for h in historial if h["rating"] == 3]
    no_gustados = [id_to_nombre.get(h["event_id"]) for h in historial if h["rating"] <= 2]

    # limpiar None (eventos no encontrados)
    f = lambda xs: [x for x in xs if x]

    partes = [f"query: {consulta}."]
    if perfil:
        partes.append(f"Perfil: {perfil}.")
    if f(encantados):
        partes.append(f"Le ha encantado (5★): {', '.join(f(encantados))}.")
    if f(gustados):
        partes.append(f"Le ha gustado (4★): {', '.join(f(gustados))}.")
    if f(regulares):
        partes.append(f"Le ha parecido regular (3★): {', '.join(f(regulares))}.")
    if f(no_gustados):
        partes.append(f"No le ha gustado (1-2★): {', '.join(f(no_gustados))}.")

    return " ".join(partes)


def construir_texto_lugar(row):
    """Texto de un candidato con prefijo 'passage:' (solo para fallback;
    en producción usamos el embedding precalculado del .npy)."""
    partes = [
        str(row.get("title", "") or ""),
        str(row.get("categoria", "") or ""),
        str(row.get("tipo_plantilla", "") or ""),
        str(row.get("description", "") or ""),
        str(row.get("municipio", "") or ""),
        str(row.get("territorio", "") or ""),
    ]
    return "passage: " + ". ".join(p.strip() for p in partes if p.strip())


# ──────────────────────────────────────────────────────────────
# VECTOR DE PERFIL (historial positivo + favoritos)
# ──────────────────────────────────────────────────────────────

def construir_vector_perfil(historial, favoritos, store, emb_consulta):
    """
    Media ponderada de embeddings de:
      - eventos del historial con rating >= 4 (peso = rating)
      - favoritos (peso = 5, rating implícito)
    Si no hay señal positiva, devuelve el vector de la consulta (fallback).
    """
    ids, pesos = [], []

    for h in historial:
        if h["rating"] >= 4:
            ids.append(h["event_id"])
            pesos.append(h["rating"])

    for ev in favoritos:
        ids.append(ev)
        pesos.append(5)

    if not ids:
        return emb_consulta

    vecs, w = [], []
    for ev, peso in zip(ids, pesos):
        v = store.vector_de_evento(ev)
        if v is not None:
            vecs.append(v)
            w.append(peso)

    if not vecs:
        return emb_consulta

    perfil = np.average(np.array(vecs), axis=0, weights=w)
    norm = np.linalg.norm(perfil)
    return perfil / norm if norm > 0 else emb_consulta


# ──────────────────────────────────────────────────────────────
# SCORING
# ──────────────────────────────────────────────────────────────

def puntuar_candidatos(candidatos_df, store, emb_consulta, emb_perfil,
                       alpha, beta, penalizaciones, multiplicadores=None):
    """
    candidatos_df: DataFrame ya filtrado por filtros duros.
    multiplicadores: {event_id: factor} para boost de promocionados.
    score = (alpha·sim_consulta + beta·sim_perfil − penalización) × multiplicador
    Devuelve lista de dicts ordenada por score (con tope de promocionados aplicado).
    """
    if candidatos_df.empty:
        return []

    multiplicadores = multiplicadores or {}

    ids = candidatos_df["id"].tolist()
    filas = [store.id_to_row.get(i) for i in ids]
    validos = [(pos, fila) for pos, fila in enumerate(filas) if fila is not None]
    if not validos:
        return []

    pos_validos = [p for p, _ in validos]
    filas_validas = [f for _, f in validos]
    M = store.matrix[filas_validas]                      # (k, dim)

    sim_consulta = M @ emb_consulta                      # (k,)
    sim_perfil   = M @ emb_perfil                        # (k,)
    score_base   = alpha * sim_consulta + beta * sim_perfil

    resultados = []
    for j, pos in enumerate(pos_validos):
        row = candidatos_df.iloc[pos]
        ev_id = int(row["id"])
        pen = penalizaciones.get(ev_id, 0.0)
        mult = multiplicadores.get(ev_id, config.MULTIPLICADOR_DEFAULT)
        score_sin_boost = float(score_base[j] - pen)
        score_final = score_sin_boost * mult
        resultados.append({
            "id":            ev_id,
            "title":         row["title"],
            "categoria":     row["categoria"],
            "municipio":     row["municipio"],
            "price":         row.get("price"),
            "imagen_url":    row.get("imagen_url"),
            "website":       row.get("website"),
            "sim_consulta":  round(float(sim_consulta[j]), 4),
            "sim_perfil":    round(float(sim_perfil[j]), 4),
            "penalizacion":  round(pen, 4),
            "multiplicador": round(mult, 2),
            "promocionado":  mult > 1.0,
            "score":         round(score_final, 4),
        })

    resultados.sort(key=lambda x: x["score"], reverse=True)
    resultados = aplicar_tope_promocionados(resultados)
    return resultados


def aplicar_tope_promocionados(resultados,
                               max_promo=config.MAX_PROMOCIONADOS,
                               top_protegido=config.TOP_PROTEGIDO):
    """
    Reordena para que no haya más de `max_promo` promocionados dentro de las
    primeras `top_protegido` posiciones. Los promocionados sobrantes se
    desplazan hacia abajo (justo tras la zona protegida), conservando el orden
    relativo del resto. No elimina nada, solo reordena.
    """
    if len(resultados) <= top_protegido:
        return resultados

    cabeza, exceso = [], []
    promo_en_cabeza = 0
    i = 0
    # construir la zona protegida respetando el tope
    while i < len(resultados) and len(cabeza) < top_protegido:
        item = resultados[i]
        if item["promocionado"] and promo_en_cabeza >= max_promo:
            exceso.append(item)          # promocionado de más: lo apartamos
        else:
            cabeza.append(item)
            if item["promocionado"]:
                promo_en_cabeza += 1
        i += 1

    resto = resultados[i:]
    # los promocionados apartados se colocan justo después de la zona protegida
    return cabeza + exceso + resto


# ──────────────────────────────────────────────────────────────
# ORQUESTADOR
# ──────────────────────────────────────────────────────────────

class Recomendador:
    """Mantiene el modelo y los embeddings cargados en memoria."""

    def __init__(self, store, model):
        self.store = store
        self.model = model

    def recomendar(self, user_id, consulta, filtros=None, top_k=config.TOP_K):
        # 1. Contexto del usuario desde SQL
        familia   = da.obtener_familia(user_id)
        favoritos = da.obtener_favoritos(user_id)
        historial = da.obtener_historial(user_id)

        # nombres para el texto del prompt (historial)
        ids_hist = [h["event_id"] for h in historial]
        id_to_nombre = da.obtener_nombres_eventos(ids_hist)

        # 2. Extraer municipio del texto libre (filtro duro) y limpiar consulta
        municipio, consulta_limpia = loc.extraer_municipio(consulta)

        # 3. Filtros duros -> candidatos (con fallback si la zona da pocos)
        candidatos = da.buscar_eventos_candidatos(filtros=filtros, municipio=municipio)
        en_zona_ids = set(candidatos["id"].tolist())
        fallback = False

        if municipio and len(candidatos) < config.MIN_RESULTADOS_ZONA:
            # completar con eventos de otras zonas (mismos filtros, sin municipio)
            fallback = True
            resto = da.buscar_eventos_candidatos(filtros=filtros, municipio=None)
            candidatos = resto  # incluye los de la zona + los de fuera

        if candidatos.empty:
            return {"user_id": user_id, "municipio": municipio,
                    "n_candidatos": 0, "resultados": []}

        # 4. Prompt + embedding de consulta (sin el municipio, ya filtrado)
        prompt = construir_prompt(consulta_limpia, familia, historial, id_to_nombre)
        emb_consulta = self.model.encode(prompt, normalize_embeddings=True)

        # 5. Vector de perfil (historial>=4 + favoritos)
        emb_perfil = construir_vector_perfil(historial, favoritos, self.store, emb_consulta)

        # 6. Penalización temporal por visitas recientes
        penalizaciones = {h["event_id"]: calcular_penalizacion(h["fecha"]) for h in historial}

        # 7. Multiplicadores de boost (promocionados) por business plan
        multiplicadores = da.obtener_multiplicadores(candidatos["id"].tolist())

        # 8. Scoring (incluye boost y tope de promocionados)
        alpha, beta = calcular_alpha_beta(len(historial))
        resultados = puntuar_candidatos(
            candidatos, self.store, emb_consulta, emb_perfil,
            alpha, beta, penalizaciones, multiplicadores
        )

        # marcar si cada resultado está dentro de la zona pedida
        if municipio:
            for r in resultados:
                r["en_zona"] = r["id"] in en_zona_ids

        return {
            "user_id":      user_id,
            "municipio":    municipio,
            "fallback":     fallback,
            "prompt":       prompt,
            "alpha":        alpha,
            "beta":         beta,
            "n_candidatos": len(candidatos),
            "resultados":   resultados[:top_k],
        }
