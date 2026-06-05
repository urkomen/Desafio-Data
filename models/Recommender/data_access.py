"""
Acceso a datos: carga de embeddings (.npy + índice CSV) y consultas a SQLite
(familia, favoritos, historial, eventos).

El .npy está normalizado (norma ~1), por lo que la similitud coseno se reduce
a un producto escalar. La fila row_idx del .npy corresponde al evento cuyo id
aparece en embeddings_index.csv (mapeo por id, no por posición, para robustez).
"""
import sqlite3
import numpy as np
import pandas as pd

import config


# ──────────────────────────────────────────────────────────────
# EMBEDDINGS (se cargan una vez al iniciar)
# ──────────────────────────────────────────────────────────────

class EmbeddingStore:
    def __init__(self, npy_path=config.EMBEDDINGS_PATH, index_path=config.INDEX_PATH):
        self.matrix = np.load(npy_path).astype(np.float32)
        self.index  = pd.read_csv(index_path)
        # id de evento -> fila en la matriz
        self.id_to_row = dict(zip(self.index["id"], self.index["row_idx"]))
        if len(self.index) != self.matrix.shape[0]:
            raise ValueError(
                f"Desalineación: index={len(self.index)} filas, "
                f"npy={self.matrix.shape[0]} filas"
            )

    def vector_de_evento(self, event_id):
        """Devuelve el embedding de un evento por su id, o None si no existe."""
        row = self.id_to_row.get(event_id)
        if row is None:
            return None
        return self.matrix[row]

    def vectores_de_eventos(self, event_ids):
        """Matriz (k, dim) con los embeddings de los ids dados (ignora los ausentes)."""
        filas = [self.id_to_row[e] for e in event_ids if e in self.id_to_row]
        if not filas:
            return np.empty((0, self.matrix.shape[1]), dtype=np.float32)
        return self.matrix[filas]


# ──────────────────────────────────────────────────────────────
# SQLITE
# ──────────────────────────────────────────────────────────────

def _conn():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def obtener_familia(user_id):
    """
    Devuelve dict con edades de los humanos y nombres de mascotas.
    Las mascotas se detectan por '(mascota)' en el campo name.
    """
    with _conn() as con:
        filas = con.execute(
            """
            SELECT m.name, m.age
            FROM families f
            JOIN family_members m ON m.family_id = f.id
            WHERE f.user_id = ?
            """,
            (user_id,),
        ).fetchall()

    edades, mascotas = [], []
    for r in filas:
        if "(mascota)" in (r["name"] or "").lower():
            mascotas.append(r["name"].replace("(mascota)", "").strip())
        else:
            edades.append(r["age"])
    return {"edades": sorted(edades), "mascotas": mascotas}


def obtener_favoritos(user_id):
    """Lista de event_id favoritos."""
    with _conn() as con:
        filas = con.execute(
            "SELECT event_id FROM user_favorite_events WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    return [r["event_id"] for r in filas]


def obtener_historial(user_id):
    """Lista de dicts {event_id, rating, fecha} del historial valorado."""
    with _conn() as con:
        filas = con.execute(
            """
            SELECT event_id, rating, selected_at
            FROM user_selected_recommendations
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchall()
    return [
        {"event_id": r["event_id"], "rating": r["rating"], "fecha": r["selected_at"]}
        for r in filas
    ]


def buscar_eventos_candidatos(filtros=None, municipio=None):
    """
    Aplica los FILTROS DUROS (flags es_* + price gratis + municipio) y devuelve
    un DataFrame con los eventos que cumplen. El scoring por coseno se hace
    después, solo sobre estos candidatos.

    filtros: dict como {"carrito": True, "gratis": True, ...}.
             Solo los True imponen condición.
    municipio: si se indica, exige municipio LIKE %municipio% (filtro duro).
    """
    filtros = filtros or {}
    where, params = [], []

    for nombre_filtro, activo in filtros.items():
        if not activo:
            continue
        if nombre_filtro == "gratis":
            placeholders = ",".join("?" * len(config.PRECIOS_GRATIS))
            where.append(f"TRIM(price) IN ({placeholders})")
            params.extend(config.PRECIOS_GRATIS)
            continue
        columna = config.FILTRO_A_COLUMNA.get(nombre_filtro)
        if columna:
            where.append(f"{columna} = 1")

    if municipio:
        where.append("LOWER(municipio) LIKE ?")
        params.append(f"%{municipio.lower()}%")

    sql = """
        SELECT id, title, description, categoria, tipo_plantilla,
               municipio, territorio, lat, lng, edad_minima,
               es_interior, es_carrito, es_cambiador, es_silla_ruedas, es_mascotas,
               price, imagen_url, website
        FROM eventos
    """
    if where:
        sql += " WHERE " + " AND ".join(where)

    with _conn() as con:
        df = pd.read_sql_query(sql, con, params=params)
    return df


def obtener_multiplicadores(event_ids):
    """
    Devuelve {event_id: multiplicador} para los eventos dados, calculado desde
    businesses.plan del negocio dueño (events.business_id -> businesses.plan ->
    config.PLAN_A_MULTIPLICADOR).

    Tolerante a esquemas incompletos: si no existe la tabla 'businesses' o la
    columna 'business_id', devuelve multiplicador 1.00 para todos (sin boost).
    """
    if not event_ids:
        return {}

    with _conn() as con:
        tablas = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        cols_ev = {c[1] for c in con.execute("PRAGMA table_info(eventos)").fetchall()}

        # Sin businesses o sin business_id -> no hay boost posible
        if "businesses" not in tablas or "business_id" not in cols_ev:
            return {e: config.MULTIPLICADOR_DEFAULT for e in event_ids}

        placeholders = ",".join("?" * len(event_ids))
        filas = con.execute(
            f"""
            SELECT e.id AS event_id, b.plan AS plan
            FROM eventos e
            LEFT JOIN businesses b ON e.business_id = b.id
            WHERE e.id IN ({placeholders})
            """,
            list(event_ids),
        ).fetchall()

    resultado = {}
    for r in filas:
        plan = r["plan"]
        resultado[r["event_id"]] = config.PLAN_A_MULTIPLICADOR.get(
            plan, config.MULTIPLICADOR_DEFAULT
        )
    for e in event_ids:
        resultado.setdefault(e, config.MULTIPLICADOR_DEFAULT)
    return resultado


def obtener_nombres_eventos(event_ids):
    """Mapeo id -> title, para construir el texto del historial/favoritos."""
    if not event_ids:
        return {}
    placeholders = ",".join("?" * len(event_ids))
    with _conn() as con:
        filas = con.execute(
            f"SELECT id, title FROM eventos WHERE id IN ({placeholders})",
            list(event_ids),
        ).fetchall()
    return {r["id"]: r["title"] for r in filas}
