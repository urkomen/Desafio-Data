"""Configuración central del recomendador."""
from pathlib import Path

# Carpeta de este archivo: .../desafio-data/recomendador
BASE_DIR = Path(__file__).resolve().parent
# Raíz del repo: .../desafio-data  (un nivel por encima)
ROOT_DIR = BASE_DIR.parent.parent
# Carpeta de datos: .../desafio-data/data
DATA_DIR = ROOT_DIR / "data"

DB_PATH         = DATA_DIR / "eventos.db"
EMBEDDINGS_PATH = DATA_DIR / "embeddings" / "embeddings.npy"
INDEX_PATH      = DATA_DIR / "embeddings" / "embeddings_index.csv"

MODELO_ST = "intfloat/multilingual-e5-large"
TOP_K     = 10

# Si un municipio filtrado deja menos de este nº de candidatos, se completa
# con eventos de otras zonas (fallback) para no devolver una lista vacía.
MIN_RESULTADOS_ZONA = 5

# Mapeo filtro de entrada (API) -> columna booleana es_* de la tabla eventos
FILTRO_A_COLUMNA = {
    "carrito":   "es_carrito",
    "cambiador": "es_cambiador",
    "interior":  "es_interior",
    "accesible": "es_silla_ruedas",
    "mascota":   "es_mascotas",
}

# "gratis" no es un flag es_*: se filtra por la columna price (texto).
# Se consideran gratis los eventos con price "0" / "0.0" / "0,0".
PRECIOS_GRATIS = {"0", "0.0", "0,0", "0.00"}

# ── Boost de eventos promocionados ─────────────────────────────
# El multiplicador se calcula desde businesses.plan (nivel contratado
# por el negocio dueño del evento). score_final = score × multiplicador.
# plan -> multiplicador. Ajusta estos valores según vuestros planes.
PLAN_A_MULTIPLICADOR = {
    1: 1.05,   # básico
    2: 1.10,   # medio
    3: 1.20,   # premium
}
MULTIPLICADOR_DEFAULT = 1.00   # eventos sin negocio / sin plan reconocido

# Tope: máximo de eventos promocionados permitidos dentro del top N.
MAX_PROMOCIONADOS = 2
TOP_PROTEGIDO     = 5          # ...dentro de las primeras 5 posiciones
