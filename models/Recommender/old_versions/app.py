"""
app.py — API Flask del recomendador de planes familiares en Euskadi
===================================================================
Endpoints:
    GET /planes          → buscar planes con filtros
    GET /planes/:id      → detalle de un lugar por external_id
    GET /health          → estado del servidor

Uso local:
    pip install flask pandas
    python app.py

Probar en Postman:
    GET http://localhost:5000/planes?ubicacion=Bilbao&lluvia=true&carrito=true&edades=bebe,1-3
    GET http://localhost:5000/planes?ubicacion=Donostia&edades=4-6&limite=5
    GET http://localhost:5000/planes?ubicacion=bizkaia&kulturklik=true
    GET http://localhost:5000/health
"""

import os
import pandas as pd
from pathlib import Path
from datetime import date
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────
# CONFIG — cambia las rutas si es necesario
# ──────────────────────────────────────────────────────────────
CSV_COMERCIOS  = os.environ.get(
    "CSV_COMERCIOS",
    "datos_ode_enriquecidos/comercios_ode_completo_2026-06-02.csv"
)
CSV_KULTURKLIK = os.environ.get(
    "CSV_KULTURKLIK",
    "datos_ode_enriquecidos/kulturklik_2026-06-02.csv"
)

# ──────────────────────────────────────────────────────────────
# LÓGICA DE INFERENCIA (igual que recomendador.py)
# ──────────────────────────────────────────────────────────────
EXCLUIDOS = {"Locales de noche", "Casinos", "Plazas de toros", "Parkings"}


# ──────────────────────────────────────────────────────────────
# CARGA DE DATOS AL ARRANCAR
# ──────────────────────────────────────────────────────────────
def cargar_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    df = df[~df["tipo_plantilla"].isin(EXCLUIDOS)].copy()
    for col in ["es_lluvia","es_carrito","es_cambiador","es_bebe","es_nino_13","es_nino_46"]:
        if col in df.columns:
            df[col] = df[col].map({"True": True, "False": False}).fillna(False)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    return df


try:
    df_comercios  = cargar_df(CSV_COMERCIOS)
    print(f"✅ Comercios cargados:  {len(df_comercios)} registros")
except FileNotFoundError:
    df_comercios  = pd.DataFrame()
    print(f"⚠  No encontrado: {CSV_COMERCIOS}")

try:
    df_kulturklik = cargar_df(CSV_KULTURKLIK)
    print(f"✅ Kulturklik cargado:  {len(df_kulturklik)} eventos")
except FileNotFoundError:
    df_kulturklik = pd.DataFrame()
    print(f"⚠  No encontrado: {CSV_KULTURKLIK}")

# Pool unificado de datos
DF = pd.concat([df_comercios, df_kulturklik], ignore_index=True) if not df_comercios.empty else df_kulturklik
print(f"✅ Pool total: {len(DF)} registros")


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def _parsear_bool(valor: str | None) -> bool:
    return str(valor).lower() in ("true", "1", "si", "yes")


def _row_to_dict(row: pd.Series) -> dict:
    d = row.to_dict()
    # Limpiar NaN/nan para JSON limpio
    return {k: (None if str(v) in ("nan","") else v) for k, v in d.items()}


# ──────────────────────────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({
        "status":       "ok",
        "total":        len(DF),
        "comercios":    len(df_comercios),
        "kulturklik":   len(df_kulturklik),
        "fecha":        str(date.today()),
    })


@app.get("/planes")
def buscar_planes():
    """
    Query params:
        ubicacion       string    "Bilbao", "bizkaia"...
        edad_max        int       edad máxima del menor (ej: 3 → lugares con edad_minima <= 3)
        lluvia          bool      true/false
        carrito         bool      true/false
        cambiador       bool      true/false
        silla_ruedas    bool      true/false
        mascotas        bool      true/false
        kulturklik      bool      incluir eventos Kulturklik (default true)
        limite          int       default 20, max 100
    """
    if DF.empty:
        abort(503, description="Sin datos. Revisa las rutas CSV_COMERCIOS y CSV_KULTURKLIK.")

    ubicacion    = request.args.get("ubicacion", "").strip()
    edad_max     = request.args.get("edad_max", None)
    lluvia       = _parsear_bool(request.args.get("lluvia"))
    carrito      = _parsear_bool(request.args.get("carrito"))
    cambiador    = _parsear_bool(request.args.get("cambiador"))
    silla_ruedas = _parsear_bool(request.args.get("silla_ruedas"))
    mascotas     = _parsear_bool(request.args.get("mascotas"))
    usar_kk      = _parsear_bool(request.args.get("kulturklik", "true"))
    limite       = min(int(request.args.get("limite", 20)), 100)

    df = DF.copy() if usar_kk else df_comercios.copy()
    df["score"] = 0

    # — Filtro ubicación —
    if ubicacion:
        ub   = ubicacion.lower()
        mask = (df["municipio"].str.lower().str.contains(ub, na=False) |
                df["territorio"].str.lower().str.contains(ub, na=False))
        df   = df[mask]

    # — Filtro edad: muestra lugares con edad_minima <= edad del niño —
    if edad_max is not None:
        try:
            edad_max_int = int(edad_max)
            df["edad_minima"] = pd.to_numeric(df["edad_minima"], errors="coerce").fillna(0)
            df = df[df["edad_minima"] <= edad_max_int]
        except ValueError:
            pass

    # — Filtros booleanos —
    if lluvia:        df = df[df["es_lluvia"]       == True]
    if carrito:       df = df[df["es_carrito"]      == True]
    if cambiador:     df = df[df["es_cambiador"]    == True]
    if silla_ruedas:  df = df[df["es_silla_ruedas"] == True]
    if mascotas:      df = df[df["es_mascotas"]     == True]

    # — Scoring —
    df = df.copy()
    if lluvia:       df["score"] += df["es_lluvia"].astype(int)
    if carrito:      df["score"] += df["es_carrito"].astype(int)
    if cambiador:    df["score"] += df["es_cambiador"].astype(int)
    if silla_ruedas: df["score"] += df["es_silla_ruedas"].astype(int)
    if mascotas:     df["score"] += df["es_mascotas"].astype(int)
    df["score"] += (df["fuente"] == "kulturklik").astype(int) * 2

    df = df.sort_values("score", ascending=False).head(limite)

    return jsonify({
        "total":     len(df),
        "filtros": {
            "ubicacion":    ubicacion    or None,
            "edad_max":     edad_max,
            "lluvia":       lluvia,
            "carrito":      carrito,
            "cambiador":    cambiador,
            "silla_ruedas": silla_ruedas,
            "mascotas":     mascotas,
            "kulturklik":   usar_kk,
        },
        "resultados": [_row_to_dict(row) for _, row in df.iterrows()],
    })


@app.get("/planes/<path:external_id>")
def detalle_plan(external_id: str):
    """Devuelve el detalle de un lugar o evento por su external_id."""
    if DF.empty:
        abort(503)
    from urllib.parse import unquote
    eid  = unquote(external_id)
    fila = DF[DF["external_id"] == eid]
    if fila.empty:
        abort(404, description=f"No encontrado: {eid}")
    return jsonify(_row_to_dict(fila.iloc[0]))


# ──────────────────────────────────────────────────────────────
# ARRANQUE
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
