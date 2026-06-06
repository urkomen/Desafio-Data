# Motor Recomendador de Planes

**Última actualización**: Junio 2026

**Versión**: 2.0

Sistema inteligente de recomendación de planes y eventos para familias basado en similitud semántica con embeddings precalculados usando `intfloat/multilingual-e5-large` (1024 dimensiones).

---



## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Características Principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Ejemplo de Uso](#-ejemplo-de-uso)
- [Configuración](#-configuración)
- [Módulos Detallados](#-módulos-detallados)
- [Desarrollo](#-desarrollo)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)

## Descripción General

El recomendador utiliza **similitud coseno** sobre embeddings multilingües para sugerir eventos personalizados. Combina:

- **Consulta del usuario** (búsqueda de texto libre)
- **Perfil familiar** (miembros, edades, mascotas)
- **Historial de experiencias** (eventos visitados con valoración)
- **Filtros duros** (accesibilidad, servicios disponibles, precio)

El sistema pondera la consulta y el perfil según la riqueza del historial, aplicando penalizaciones temporales para evitar repeticiones recientes.

---

## Características Principales

* **Recomendaciones personalizadas** basadas en historial y perfil familiar
* **Búsqueda semántica multilingüe** con embeddings precalculados
* **Filtros accesibles** (carrito, cambiador, interior, accesible, mascotas, gratis)
* **Detección automática de ubicación** desde texto libre
* **Boosting de eventos promocionados** según plan de negocio
* **Penalización temporal** para evitar repetir lugares recientes
* **API REST** con carga lazy del modelo (eficiencia de memoria)

---

## Arquitectura

### Flujo de Recomendación

```
1. Usuario envía: id_user + consulta (texto) + filtros
                ↓
2. Construcción de prompt enriquecido: 
   - Consulta original
   - Información familiar (edades, mascotas)
   - Historial ponderado por rating (≥4 estrellas)
   - Eventos favoritos (rating implícito 5)
                ↓
3. Cálculo de vector de perfil: 
   - Media ponderada de embeddings del historial + favoritos
                ↓
4. Filtros duros: reduce pool de eventos (accesibilidad, precio, servicios)
                ↓
5. Scoring final:
   - Score = α·sim(consulta) + β·sim(perfil) - penalización_temporal
   - α/β varían según tamaño del historial (curva adaptativa)
                ↓
6. Boosting y ranking:
   - Multiplicadores según plan del negocio (1.05 → 1.20)
   - Top K=10 eventos (configurable)
   - Fallback geográfico si hay pocos resultados
```

### Ponderación Dinámica (α, β)

| Historial    | α (consulta) | β (perfil) | Justificación                 |
| ------------ | ------------- | ----------- | ------------------------------ |
| < 3 eventos  | 0.90          | 0.10        | Prioriza búsqueda específica |
| 3-10 eventos | 0.70          | 0.30        | Balance inicial                |
| > 10 eventos | 0.50          | 0.50        | Perfil bien definido           |

---

## Estructura de Archivos

```
models/Recommender/
├── app.py              # API Flask - endpoint POST /recomendar
├── recommender.py      # Lógica de recomendación y scoring
├── config.py           # Configuración centralizada (rutas, modelo, constantes)
├── data_access.py      # Acceso a SQLite y carga de embeddings (.npy + índice)
├── location.py         # Detección automática de municipio en texto libre
├── requirements.txt    # Dependencias Python
├── README.md           # Este archivo
└── old_version/        # Versiones antiguas (deprecated)
```

### Datos Esperados

El sistema espera los siguientes archivos en `../data/`:

- `eventos.db` — Base de datos SQLite con eventos, familias, historial
- `embeddings/embeddings.npy` — Matriz de embeddings (normalizada, norma ~1)
- `embeddings/embeddings_index.csv` — Mapeo de id_evento → row_idx

---

## Instalación y Ejecución

### Requisitos Previos

- Python 3.8+
- pip o conda

### Instalación

```bash
# 1. Navegar a la carpeta del recomendador
cd models/Recommender

# 2. Instalar dependencias
pip install -r requirements.txt
# Nota: Descargará automáticamente el modelo ST (~500 MB) en la primera ejecución
```

### Ejecutar la API

```bash
python app.py
```

**Salida esperada:**

```
Cargando embeddings...
Cargando modelo intfloat/multilingual-e5-large (puede tardar la primera vez)...
 * Running on http://127.0.0.1:5000
```

- **Primera ejecución**: ~30-60 segundos (descarga modelo ST ~500 MB, carga embeddings ~2 GB)
- **Siguientes ejecuciones**: ~5-10 segundos (modelo cacheado localmente)

---

## Ejemplo de Uso

### Endpoint

```
POST http://localhost:5000/recomendar
Content-Type: application/json
```

### Request

```bash
curl -X POST http://localhost:5000/recomendar \
  -H "Content-Type: application/json" \
  -d '{
    "id_user": 10,
    "consulta": "Museo Bilbao planes en familia",
    "filtros": {
      "carrito": true,
      "cambiador": false,
      "interior": true,
      "accesible": false,
      "mascota": true,
      "gratis": false
    }
  }'
```

### Response (200 OK)

```json
{
  "recomendaciones": [
    {
      "evento_id": 1234,
      "nombre": "Museo Guggenheim Bilbao",
      "municipio": "Bilbao",
      "score": 0.8756,
      "ranking": 1,
      "razon": "Alta similitud con tu búsqueda y perfil familiar"
    },
    {
      "evento_id": 5678,
      "nombre": "Jardín Botánico",
      "municipio": "Bilbao",
      "score": 0.8234,
      "ranking": 2,
      "razon": "Coincide con tus preferencias"
    }
    // ... hasta 10 resultados
  ],
  "total": 42,
  "filtrados": 35
}
```

---

## Configuración

Editar `config.py` para personalizar:

```python
# Modelo de embeddings (multilingüe)
MODELO_ST = "intfloat/multilingual-e5-large"

# Número de recomendaciones a devolver
TOP_K = 10

# Umbral mínimo de resultados por zona
# Si hay < 5 eventos en la zona filtrada, completa con eventos de otras zonas
MIN_RESULTADOS_ZONA = 5

# Boost de eventos promocionados por plan de negocio
PLAN_A_MULTIPLICADOR = {
    1: 1.05,    # Plan básico → +5%
    2: 1.10,    # Plan medio → +10%
    3: 1.20,    # Plan premium → +20%
}

# Máximo de eventos promocionados en el top 5
MAX_PROMOCIONADOS = 2
TOP_PROTEGIDO = 5

# Penalización temporal por lugares ya visitados
# Decae linealmente de 0.3 a 0 en 90 días
```

---

## Módulos Detallados

### `app.py`

- API REST con Flask
- Endpoint: `POST /recomendar`
- Inicialización **lazy** del modelo (no carga en importación)
- Manejo de errores y validación

### `recommender.py`

- **Construcción de prompts enriquecidos** con contexto familiar
- **Cálculo de vector de perfil** desde historial ponderado
- **Scoring multicriteria**: α·similitud(consulta) + β·similitud(perfil) - penalización
- **Adaptación dinámica** del peso consulta/perfil según historial

### `data_access.py`

- Carga de embeddings `.npy` normalizados
- Mapeo eficiente id_evento → índice de fila
- Consultas SQLite para:
  - Datos familiares (edades, mascotas)
  - Historial de eventos (ratings)
  - Eventos favoritos
  - Información de eventos (filtros, precio)

### `location.py`

- Detección automática de municipio desde texto libre
- Normalización (minúsculas, sin acentos)
- Manejo de **alias bilingües** (ej: "Donostia / San Sebastián")
- Priorización de matches más largos (evita falsos positivos)

### `config.py`

- Rutas centralizadas (embeddings, BD, modelo)
- Mapeo filtro API → columna SQLite
- Constantes de scoring y boosting
- Definición de "gratis" (precios: "0", "0.0", "0,0")

---

## Desarrollo

### Testing

El módulo `app.py` permite pasar un `stub_model` para tests:

```python
from models.Recommender import app

stub_model = MockSentenceTransformer()
app.init(stub_model=stub_model)
```

### Dependencias

| Paquete               | Versión | Uso                             |
| --------------------- | -------- | ------------------------------- |
| Flask                 | ≥3.0    | API REST                        |
| numpy                 | ≥1.24   | Álgebra matricial, embeddings  |
| pandas                | ≥2.0    | Indexación, consultas de datos |
| sentence-transformers | ≥2.2    | Modelo multilingüe ST          |

---

## Performance

- **Tiempo de carga (primera vez)**: ~30-60s
- **Tiempo de inferencia (por request)**: ~200-500ms
- **Memoria RAM**: ~2.5 GB (modelo + embeddings)
- **Tamaño modelo**: ~500 MB (descargado automáticamente)
- **Tamaño embeddings**: ~2 GB (.npy + índice CSV)

### Optimizaciones Implementadas

Carga lazy del modelo (no se carga hasta primer request)
Embeddings normalizados (similitud coseno = producto escalar)
Índice CSV para mapeo robusto id → fila
Multiplicadores en top 5 protegido (limita boost de promocionados)

---

## Troubleshooting

### Error: "Model not found" o descarga lenta

→ Primera ejecución descarga el modelo (~500 MB). Requiere conexión a internet.

### Error: "Desalineación: index != npy"

→ Los archivos de embeddings están corruptos. Regenerar desde `notebooks/embedder_multilingual_e5.ipynb`

### Recomendaciones no personalizadas / Histórico vacío

→ Verificar en BD que el usuario tiene eventos en su historial (tabla `user_events`)

### Municipio no detectado

→ Comprobar `location.py`: revisar catálogo de alias y normalización en `location._normalizar()`
