# Documentación técnica — Recomendador PlanGune

## Control de versiones y modificaciones

| Versión | Fecha      | Autor                         | Descripción                                                                                                                                                                                            |
| -------- | ---------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1      | 2026-06-03 | ChatGPT (edición solicitada) | Se añaden arquitectura ampliada, esquema de BBDD, OpenAPI/Swagger, ejemplos adicionales, entrenamiento IA, dependencias, variables de entorno, pipeline reproducible, limitaciones y roadmap técnico. |
| 1.0      | 2026-06-03 | Urko Menendez                 | Plantilla de versión base del documento.                                                                                                                                                               |

---

## Índice

1. [Visión general del sistema](#1-visión-general-del-sistema)
2. [Arquitectura](#2-arquitectura)
3. [API de Data Science — Referencia de endpoints](#3-api-de-data-science--referencia-de-endpoints)
4. [Pipeline de datos y ETL](#4-pipeline-de-datos-y-etl)
5. [Motor de IA: NLP y recomendación](#5-motor-de-ia-nlp-y-recomendación)
6. [Seguridad y cumplimiento](#6-seguridad-y-cumplimiento)
7. [Despliegue e infraestructura](#7-despliegue-e-infraestructura)
8. [Runbook operacional](#8-runbook-operacional)
9. [Guía de desarrollo local (DS)](#9-guía-de-desarrollo-local-ds)
10. [Anexos](#10-anexos)

---

## 1. Visión general del sistema

### Propósito

Sistema de recomendación de lugares, establecimientos y actividades en el País Vasco que entiende **lenguaje natural, contexto geográfico/familiar y gustos**. Permite a usuarios como Ainhoa (Barakaldo) o Jaime (Getxo) encontrar planes para el fin de semana con bebés y niños pequeños sin fricción de búsqueda.

### Usuarios objetivo

| Persona                | Perfil                                            | Necesidad clave                                                                                        |
| ---------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Ainhoa, 32 (Barakaldo) | Familia con bebé de meses                        | Lugares accesibles con silla, cambiador, sin ruido                                                     |
| Jaime, 40 (Getxo)      | Familia con niño de 3 años                      | Actividades cortas, bien conectadas, que aguanten el ritmo de un peque                                 |
| Leire, 38 (Durango)    | Familia monomarental con dos hijos de 7 y 5 años | Agenda cultural pública, teatros de calle, acceso libre a museos municipales o eventos subvencionados |
|                        |                                                   |                                                                                                        |

### Stack tecnológico

| Capa               | Tecnología                         | Notas                        |
| ------------------ | ----------------------------------- | ---------------------------- |
| LLM / NLP          | Claude Sonnet (Anthropic API)       | Extracción de intención    |
| Embeddings         | `multilingual-e5-large`           | Soporta ES + EU              |
| Vector store       | ChromaDB / FAISS                    | Colección:`places_bilbao` |
| DS API             | FastAPI 0.111 (Python 3.11)         | Puerto interno 8001          |
| Backend principal  | FastAPI (Full Stack)                | Puerto 8000                  |
| Frontend           | React + Leaflet + GEO-EUSKADI tiles | Puerto 3000                  |
| Cache              | Redis                               | TTL configurable             |
| Infraestructura    | Docker Compose                      | 1 `compose.yml` en raíz   |
| Datos geográficos | GEO-EUSKADI WFS/WMS + OpenStreetMap | ETRS89 → WGS84              |

---

## 2. Arquitectura

### Diagrama de componentes

```
[Usuario]
    │ query NL + ubicación
    ▼
[Frontend React] ──► [Backend Full Stack :8000]
                              │
                   ┌──────────┴──────────┐
                   │                     │
              [Redis Cache]       [DS API :8001]
                                         │
                         ┌───────────────┼────────────────┐
                         │               │                │
                  [NLP Engine]   [ChromaDB :8002]   [ETL pipeline]
                  (LLM + prompts)  (embeddings)   (GEO-EUSKADI WFS)
```

### Flujo de una petición

```
1. Usuario escribe query → Frontend
2. Frontend → POST /api/recommend (backend FS)
3. Backend FS → POST /recommend (DS API interna)
4. DS API:
   a. NLP Engine extrae intención estructurada
   b. Búsqueda semántica en ChromaDB (ANN)
   c. Scoring híbrido + re-ranking
   d. Devuelve lista rankeada con justificación
5. Backend FS aplica auth, cache, logging
6. Frontend renderiza tarjetas + mapa
```

### Entornos

| Entorno     | DS API          | Backend            | Propósito        |
| ----------- | --------------- | ------------------ | ----------------- |
| Local       | localhost:8001  | localhost:8000     | Desarrollo        |
| Staging     | ds-staging:8001 | staging.app        | QA / integración |
| Producción | ds-prod:8001    | app.euskadi-fam.es | Producción       |

---

## 3. API de Data Science — Referencia de endpoints

> **Audiencia principal: Full Stack**
> La DS API es **interna** — no expuesta a Internet directamente.

### Base URL

```
http://ds-api:8001     ← desde la red Docker interna
http://localhost:8001  ← en desarrollo local
```

### Autenticación

Todas las peticiones incluyen el header:

```http
X-Internal-Token: <token>
```

El token lo provisiona Ciberseguridad vía secrets. Ver sección 6.

---

### `POST /recommend`

Recomendación personalizada a partir de lenguaje natural y contexto.

**Request body:**

```json
{
  "query": "algo tranquilo mañana en Bilbao con bebé y niño de 3 años",
  "user_location": {
    "lat": 43.2627,
    "lon": -2.9253
  },
  "max_results": 5,
  "context": {
    "weather": "rain",
    "day_of_week": "saturday",
    "family_profile": {
      "baby_months": 6,
      "children_ages": [3]
    }
  }
}
```

**Campos obligatorios:** `query`, `user_location`
**Campos opcionales:** `max_results` (default: 5), `context`

**Response 200 OK:**

```json
{
  "results": [
    {
      "id": "geu_001234",
      "name": "Museo Marítimo de Bilbao",
      "category": "museo",
      "score": 0.89,
      "distance_km": 1.2,
      "tags": ["indoor", "baby_friendly", "cambiador", "accesible_silla"],
      "justification": "Espacio interior accesible con silla de ruedas y zona de cambiador.",
      "coordinates": { "lat": 43.2630, "lon": -2.9290 },
      "opening_hours": "10:00-20:00",
      "address": "Muelle Ramón de la Sota, 1, Bilbao"
    }
  ],
  "intent": {
    "category": "cultural",
    "max_distance_km": 5.0,
    "requires_indoor": true,
    "baby_accessible": true,
    "noise_tolerance": "low"
  },
  "query_id": "q_abc123",
  "latency_ms": 420
}
```

**Errores:**

| Código | Motivo                            | Acción recomendada                |
| ------- | --------------------------------- | ---------------------------------- |
| 400     | Query vacía o malformada         | Validar input antes de llamar      |
| 422     | Coordenadas fuera del País Vasco | Verificar que lat/lon son válidos |
| 429     | Rate limit superado               | Esperar 1s y reintentar            |
| 503     | Vector store no disponible        | Llamar a `/health` y alertar     |

---

### `GET /search`

Búsqueda directa por texto sin procesamiento de contexto familiar. Útil para el buscador rápido.

```
GET /search?q=restaurante+getxo&limit=10
```

**Response:** mismo schema que `/recommend` pero sin campo `intent`.

---

### `GET /places/{id}`

Detalle completo de un lugar por ID interno.

```
GET /places/geu_001234
```

**Response:** objeto `place` completo (ver esquema en sección 4).

---

### `GET /health`

Estado del sistema. Llamar antes de alertar en caso de degradación.

```json
{
  "status": "ok",
  "vector_store": "ok",
  "llm_api": "ok",
  "data_freshness": "2024-01-15T08:00:00Z",
  "places_indexed": 487,
  "version": "0.1.0"
}
```

---

### Notas de integración para Full Stack

- La DS API **no gestiona sesión de usuario** — el token de usuario lo verifica el backend FS antes de llamar a DS.
- El campo `query_id` es efímero (no persiste). Si se quiere analytics de queries, el backend FS debe logarlo en su propia capa.
- En caso de timeout (>1.5s), devolver al frontend los resultados en caché de Redis si existen.

---

## 4. Pipeline de datos y ETL

> **Audiencia principal: Data Science**
> Secundaria: Full Stack (para entender el modelo de datos)

### Fuentes de datos

| Fuente        | Protocolo    | Actualización            | Notas                                   |
| ------------- | ------------ | ------------------------- | --------------------------------------- |
| GEO-EUSKADI   | WFS 2.0      | Semanal (lunes 06:00 UTC) | Necesita conversión ETRS89 → WGS84    |
| OpenStreetMap | Overpass API | Semanal                   | Complemento para hostelería y comercio |
| Google Places | REST API     | Bajo demanda              | Valoraciones y detalles adicionales     |

### Capas GEO-EUSKADI usadas

| Capa WFS                  | Contenido                                     |
| ------------------------- | --------------------------------------------- |
| `recursos_turisticos`   | Alojamientos, restaurantes, atracciones       |
| `espacios_culturales`   | Museos, centros culturales, bibliotecas       |
| `parques_naturales`     | Parques, espacios naturales, playas           |
| `servicios_municipales` | Servicios públicos, instalaciones deportivas |

### Proceso ETL paso a paso

```
Paso 1 — Ingesta raw
  └── Script: ds/pipeline/01_ingest.py
  └── Output: data/raw/geo_euskadi_{YYYYMMDD}.json
  └── Comando: python 01_ingest.py --layers all --date 2024-01-15

Paso 2 — Normalización y limpieza
  └── Script: ds/pipeline/02_clean.py
  └── Convierte ETRS89 → WGS84, deduplicación, normaliza nombres ES/EU
  └── Output: data/clean/places_{YYYYMMDD}.json

Paso 3 — Enriquecimiento familiar
  └── Script: ds/pipeline/03_enrich.py
  └── Añade tags: baby_friendly, cambiador, indoor, accesible_silla, etc.
  └── Estrategia: reglas + LLM para ambiguos
  └── Output: data/enriched/places_{YYYYMMDD}.json

Paso 4 — Indexación en ChromaDB
  └── Script: ds/pipeline/04_index.py
  └── Genera embeddings y carga en colección places_bilbao
  └── Tiempo estimado: ~10 min para 500 lugares
```

### Esquema de un lugar enriquecido

```json
{
  "id": "geu_001234",
  "name": "Parque Doña Casilda",
  "category": "parque",
  "subcategory": "espacio_natural",
  "coordinates": { "lat": 43.2675, "lon": -2.9402 },
  "address": "C/ Músico Leizaola, Bilbao",
  "source": "geo_euskadi",
  "tags": {
    "baby_friendly": true,
    "cambiador": false,
    "accesible_silla": true,
    "indoor": false,
    "menu_infantil": false,
    "zona_juegos": true,
    "parking_cercano": true,
    "noise_level": "low"
  },
  "description_es": "Parque urbano en el centro de Bilbao...",
  "description_eu": "Bilboko hiri parkea...",
  "opening_hours": "24h",
  "last_updated": "2024-01-15"
}
```

### Ejecutar el pipeline completo manualmente

```bash
cd ds/pipeline
python 01_ingest.py --layers all
python 02_clean.py
python 03_enrich.py
python 04_index.py --rebuild

# O con el wrapper completo:
python run_pipeline.py --all --rebuild-index
```

### Criterios de calidad de datos

Antes de indexar, `04_index.py` valida que:

- Al menos 400 lugares indexados
- < 5% de lugares sin coordenadas válidas
- < 10% de lugares sin ningún tag de accesibilidad

Si no se cumplen, el script aborta y mantiene el índice anterior.

---

## 5. Motor de IA: NLP y recomendación

> **Audiencia principal: Data Science**

### NLP Engine — extracción de intención

Convierte una query en lenguaje libre en un objeto de intención estructurado.

**Modelo:** Claude claude-sonnet-4-6 (Anthropic API)**Prompt:** `ds/nlp/prompts/intent_extraction_v1.txt` (versionado en git)

> ⚠️ No modificar prompts en producción sin pasar por evaluación (`run_eval.py`). Ver proceso en sección 9.

**Intent schema (Pydantic):**

```python
class Intent(BaseModel):
    category: Literal["parque", "museo", "restaurante", "actividad", "playa", "otro"]
    max_distance_km: float = 5.0
    requires_indoor: bool = False
    baby_accessible: bool = False
    noise_tolerance: Literal["low", "medium", "high"] = "medium"
    time_of_day: Literal["morning", "afternoon", "any"] = "any"
    weather_dependent: bool = False
    free_text_filters: list[str] = []   # Ej: ["tranquilo", "con parking"]
```

### Embeddings

| Parámetro            | Valor                                     |
| --------------------- | ----------------------------------------- |
| Modelo                | `paraphrase-multilingual-MiniLM-L12-v2` |
| Idiomas               | Español + Euskera                        |
| Dimensión            | 384                                       |
| Colección ChromaDB   | `places_bilbao`                         |
| Script de indexación | `ds/pipeline/04_index.py`               |

### Motor de recomendación híbrido

```
score_final = w1·sem_sim + w2·tag_match - w3·dist_penalty + w4·ctx_boost - w5·div_penalty
```

**Pesos por defecto** (`ds/recommender/weights.yaml`):

```yaml
semantic_similarity:  0.40
tag_match:            0.25
distance_penalty:     0.20
context_boost:        0.10
diversity_penalty:    0.05
```

**Penalización por distancia:**

- 0-3 km: sin penalización
- 3-8 km: −0.15
- > 8 km: −0.40
  >

**Re-ranking de diversidad (MMR):**

- Penaliza categorías repetidas en los primeros resultados
- Factor configurable vía `weights.yaml → diversity_penalty`

### Evaluación del modelo

**Dataset de evaluación:** `ds/eval/test_queries.json` — 50 queries con resultados esperados.

**Métricas objetivo:**

| Métrica               | Objetivo          |
| ---------------------- | ----------------- |
| Precision@3            | > 0.75            |
| Diversity index        | > 0.60            |
| Latencia P95           | < 800ms           |
| Baby accessible recall | > 0.90 (crítico) |

**Ejecutar evaluación:**

```bash
cd ds
python eval/run_eval.py --weights recommender/weights.yaml
# Genera reporte en: eval/reports/report_{timestamp}.json
```

---

## 6. Seguridad y cumplimiento

> **Audiencia principal: Ciberseguridad**
> Secundaria: Full Stack, Data Science

### Autenticación y autorización

- La DS API **no está expuesta a Internet**. Solo accesible desde la red Docker interna.
- El backend Full Stack autentica al usuario (JWT) antes de llamar a DS.
- La comunicación Backend FS → DS API usa un token interno estático en header `X-Internal-Token`.
- Rotación de token interno: cada 30 días. Responsable: Ciberseguridad.

### Gestión de secrets

| Secret                | Scope            | Propietario | Almacenamiento   |
| --------------------- | ---------------- | ----------- | ---------------- |
| `ANTHROPIC_API_KEY` | DS API           | DS          | `.env` / vault |
| `GOOGLE_PLACES_KEY` | ETL pipeline     | DS          | `.env` / vault |
| `INTERNAL_DS_TOKEN` | Backend FS ↔ DS | Ciber       | `.env` / vault |
| `REDIS_PASSWORD`    | Backend FS + DS  | Ciber       | `.env` / vault |
| `JWT_SECRET`        | Backend FS       | Full Stack  | `.env` / vault |

> **Regla:** NUNCA commitear secrets al repositorio. Usar `.env.example` como plantilla sin valores reales.

### Datos personales y GDPR

| Dato                   | ¿Se almacena?    | Dónde    | TTL                 |
| ---------------------- | ----------------- | --------- | ------------------- |
| Query de usuario       | No por defecto    | —        | —                  |
| Coordenadas de usuario | No                | —        | —                  |
| `query_id`           | Efímero (RAM)    | —        | Duración petición |
| Logs de error          | Sí, anonimizados | `/logs` | 30 días            |

Para activar logging extendido en debugging:

```bash
LOG_LEVEL=DEBUG LOG_ANONYMIZE=true docker compose up ds-api
```

### Superficie de ataque de la DS API

- Input validation en todos los endpoints con Pydantic (tipos + rangos).
- Rate limiting: 100 req/min por IP interna.
- El LLM solo genera JSON estructurado — sin ejecución de código ni acceso a FS.
- Coordenadas validadas: solo se aceptan dentro del bounding box del País Vasco.
  - `lat: [42.5, 43.5]`, `lon: [-3.5, -1.5]`

### Checklist de seguridad antes de producción

- [ ] Secrets en vault, no en `.env` de producción
- [ ] HTTPS en todos los servicios externos
- [ ] Token interno rotado desde staging
- [ ] Rate limiting verificado en staging
- [ ] Logs de producción con `LOG_ANONYMIZE=true`
- [ ] ChromaDB sin puerto expuesto externamente
- [ ] Revisión de dependencias Python (`pip audit`)

---

## 7. Despliegue e infraestructura

> **Audiencia: todos los equipos**

### Requisitos de sistema

| Requisito      | Mínimo | Recomendado |
| -------------- | ------- | ----------- |
| RAM            | 8 GB    | 16 GB       |
| CPU            | 4 cores | 8 cores     |
| Disco          | 10 GB   | 20 GB       |
| Docker         | 24+     | 25+         |
| Docker Compose | 2.20+   | 2.24+       |

### Arrancar el stack completo

```bash
git clone <repo-url>
cd euskadi-fam
cp .env.example .env
# Editar .env con los valores reales (ver sección 6)
docker compose up -d
docker compose logs -f    # seguir logs
```

### Servicios del compose

| Servicio     | Puerto         | Descripción               |
| ------------ | -------------- | -------------------------- |
| `ds-api`   | 8001 (interno) | FastAPI Data Science       |
| `backend`  | 8000           | FastAPI Full Stack         |
| `chromadb` | 8002 (interno) | Vector store               |
| `redis`    | 6379 (interno) | Cache                      |
| `frontend` | 3000           | React (dev) / nginx (prod) |

### Variables de entorno principales

```bash
# DS API
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
CHROMA_HOST=chromadb
CHROMA_PORT=8002
CHROMA_COLLECTION=places_bilbao
MAX_RESULTS_DEFAULT=5
LOG_LEVEL=INFO
LOG_ANONYMIZE=true

# Compartidas
INTERNAL_DS_TOKEN=...
REDIS_PASSWORD=...
REDIS_HOST=redis
REDIS_TTL_SECONDS=3600
```

### Primera carga de datos

Tras arrancar el stack por primera vez (ChromaDB vacío):

```bash
docker compose exec ds-api python pipeline/run_pipeline.py --all --rebuild-index
```

Esto puede tardar 10-15 minutos. Verificar con:

```bash
curl http://localhost:8001/health
# Esperar: "places_indexed": 400+
```

### Actualización de datos (semanal)

```bash
docker compose exec ds-api python pipeline/run_pipeline.py --all --rebuild-index
```

Configurado como tarea cron los lunes a las 06:00 UTC en producción.

---

## 8. Runbook operacional

> **Audiencia: todos los equipos (turno de guardia)**

### Verificar estado del sistema

```bash
# Estado de todos los servicios
docker compose ps

# Estado del DS API (incluye vector store y LLM)
curl http://localhost:8001/health | python -m json.tool

# Logs de los últimos 100 eventos
docker compose logs --tail=100 ds-api
```

### Síntomas comunes y soluciones

| Síntoma                                     | Causa probable                           | Acción                                                                          |
| -------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| `/health` devuelve `vector_store: error` | ChromaDB caído                          | `docker compose restart chromadb && sleep 10 && docker compose restart ds-api` |
| `/recommend` responde >2s                  | LLM API lenta o saturada                 | Comprobar[status.anthropic.com](https://status.anthropic.com)                       |
| Resultados irrelevantes o escasos            | Datos desactualizados o índice corrupto | Ejecutar pipeline completo (ver 7)                                               |
| `llm_api: error` en `/health`            | API key expirada o inválida             | Rotar `ANTHROPIC_API_KEY` en `.env` y `docker compose restart ds-api`      |
| `places_indexed: 0`                        | Índice vacío (primera vez o borrado)   | Ejecutar `run_pipeline.py --rebuild-index`                                     |

### Rollback de pesos del recomendador

Si tras un cambio de `weights.yaml` la calidad de resultados cae:

```bash
# En el contenedor
docker compose exec ds-api cp recommender/weights.yaml.bak recommender/weights.yaml
docker compose restart ds-api
```

### Rollback de prompt NLP

```bash
# Los prompts están versionados en git
git log ds/nlp/prompts/intent_extraction_v1.txt
git checkout <commit-anterior> -- ds/nlp/prompts/intent_extraction_v1.txt
docker compose exec ds-api cp /app/ds/nlp/prompts/intent_extraction_v1.txt /data/prompts/
docker compose restart ds-api
```

### Reiniciar el índice de cero

Solo si hay corrupción confirmada:

```bash
docker compose stop ds-api chromadb
docker volume rm euskadi-fam_chromadb-data
docker compose up -d chromadb
sleep 10
docker compose up -d ds-api
docker compose exec ds-api python pipeline/run_pipeline.py --all --rebuild-index
```

---

## 9. Guía de desarrollo local (DS)

> **Audiencia principal: Data Science**

### Setup del entorno

```bash
git clone <repo-url>
cd euskadi-fam/ds

python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
# Editar .env con ANTHROPIC_API_KEY y GOOGLE_PLACES_KEY
```

### Arrancar la DS API en local

```bash
uvicorn app.main:app --reload --port 8001
# Swagger UI: http://localhost:8001/docs
```

Requiere ChromaDB corriendo. Para solo ChromaDB:

```bash
docker compose up -d chromadb redis
```

### Ejecutar tests

```bash
# Tests unitarios
pytest ds/tests/ -v

# Tests de integración (requiere ChromaDB y Anthropic API key)
pytest ds/tests/integration/ -v -m integration

# Evaluación del modelo (lento ~3 min)
pytest ds/eval/ -v -m eval
```

### Proceso para modificar prompts

Los prompts afectan directamente la calidad de resultados. Protocolo obligatorio:

1. Editar prompt en `ds/nlp/prompts/intent_extraction_v1.txt`
2. Ejecutar evaluación: `python eval/run_eval.py`
3. Verificar que **Precision@3 > 0.75** y **Baby accessible recall > 0.90**
4. Documentar el cambio en `ds/nlp/prompts/CHANGELOG.md`
5. Abrir PR con los resultados del eval adjuntos

### Proceso para ajustar pesos del recomendador

1. Editar `ds/recommender/weights.yaml`
2. Ejecutar: `python eval/run_eval.py --weights recommender/weights.yaml`
3. Comparar con baseline: `python eval/compare.py --new report_nuevo.json --base report_base.json`
4. Si mejora: commit + PR. Si no mejora: revertir.

### Estructura de directorios DS

```
ds/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── routers/             # Endpoints (/recommend, /search, /health)
│   ├── models/              # Pydantic schemas
│   └── services/
│       ├── nlp.py           # NLP Engine
│       ├── recommender.py   # Motor de recomendación
│       └── vector_store.py  # Interfaz ChromaDB
├── pipeline/
│   ├── 01_ingest.py
│   ├── 02_clean.py
│   ├── 03_enrich.py
│   ├── 04_index.py
│   └── run_pipeline.py      # Wrapper completo
├── nlp/
│   └── prompts/
│       ├── intent_extraction_v1.txt
│       └── CHANGELOG.md
├── recommender/
│   └── weights.yaml
├── eval/
│   ├── test_queries.json
│   ├── run_eval.py
│   └── compare.py
├── tests/
│   ├── unit/
│   └── integration/
├── data/                    # .gitignore — no commitear datos
│   ├── raw/
│   ├── clean/
│   └── enriched/
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## 10. Anexos

### A. Glosario

| Término                         | Definición                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Intent**                 | Objeto estructurado extraído de una query NL. Contiene categoría, filtros y preferencias.      |
| **Embedding**              | Vector numérico de 384 dimensiones que representa semánticamente un texto.                     |
| **ANN**                    | Approximate Nearest Neighbor. Búsqueda de vectores similares en ChromaDB/FAISS.                 |
| **Re-ranking**             | Reordenación final de candidatos aplicando contexto, diversidad y reglas de negocio.            |
| **MMR**                    | Maximal Marginal Relevance. Algoritmo que balancea relevancia y diversidad en los resultados.    |
| **WFS**                    | Web Feature Service. Protocolo estándar OGC para datos geoespaciales vectoriales (GEO-EUSKADI). |
| **ETRS89**                 | European Terrestrial Reference System 1989. Sistema de coordenadas que usa GEO-EUSKADI.          |
| **WGS84**                  | World Geodetic System 1984. Sistema de coordenadas estándar GPS (Google Maps, Leaflet).         |
| **Baby accessible recall** | Porcentaje de lugares realmente accesibles con bebé que el sistema recupera correctamente.      |

### B. Contactos por área

| Área                       | Responsable           | Canal             |
| --------------------------- | --------------------- | ----------------- |
| DS API / modelos / pipeline | Equipo Data Science   | `#ds-squad`     |
| Frontend / integración API | Equipo Full Stack     | `#frontend`     |
| Auth / secrets / GDPR       | Equipo Ciberseguridad | `#ciber`        |
| Alertas de producción      | Todos                 | `#alertas-prod` |

### C. Registro de cambios

| Versión | Fecha    | Autor   | Cambio                 |
| -------- | -------- | ------- | ---------------------- |
| 0.1      | Sprint 1 | DS Team | Documentación inicial |
|          |          |         |                        |

### D. Decisiones técnicas relevantes (ADR ligero)

| Decisión                          | Alternativa descartada     | Motivo                                                                |
| ---------------------------------- | -------------------------- | --------------------------------------------------------------------- |
| ChromaDB como vector store         | Pinecone, Weaviate         | Sin dependencia cloud, funciona en local y Docker                     |
| `paraphrase-multilingual-MiniLM` | `text-embedding-ada-002` | Soporta Euskera, sin coste por embedding, suficiente para 500 lugares |
| FastAPI para DS API                | Flask, Django              | Async nativo, Pydantic integrado, OpenAPI automático                 |
| Pesos en YAML                      | Base de datos              | Rollback trivial, versionable en git, suficiente para v0.1            |

---

*Documento mantenido por el equipo de Data Science. Cualquier corrección o mejora: PR a `docs/tecnica/`.*

---

## 11. Esquema de Base de Datos

### Modelo lógico principal

```sql
TABLE places (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    address TEXT,
    source VARCHAR(50),
    description_es TEXT,
    description_eu TEXT,
    opening_hours TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

TABLE place_tags (
    id BIGINT PRIMARY KEY,
    place_id VARCHAR(50) REFERENCES places(id),
    tag_name VARCHAR(100),
    tag_value VARCHAR(100)
);

TABLE queries_audit (
    id BIGINT PRIMARY KEY,
    query_id VARCHAR(100),
    timestamp TIMESTAMP,
    latency_ms INTEGER,
    status VARCHAR(50)
);
```

### Relación con ChromaDB

- Tabla lógica `places` → fuente maestra.
- ChromaDB almacena embeddings asociados al `place_id`.
- Reindexación completa mediante `04_index.py`.

---

## 12. OpenAPI / Swagger

FastAPI genera automáticamente la especificación OpenAPI.

### URLs

```text
Swagger UI:
http://localhost:8001/docs

OpenAPI JSON:
http://localhost:8001/openapi.json

ReDoc:
http://localhost:8001/redoc
```

### Versionado

- OpenAPI: 3.1
- FastAPI: 0.111+
- Compatibilidad REST JSON

---

## 13. Dependencias y Versiones

### Dependencias principales

```text
Python 3.11
FastAPI 0.111+
Uvicorn 0.30+
Pydantic 2.x
ChromaDB 0.5+
Redis 7.x
sentence-transformers 3.x
Anthropic SDK latest estable
Docker 24+
Docker Compose 2.20+
```

### Variables de entorno obligatorias

```bash
ANTHROPIC_API_KEY=
GOOGLE_PLACES_KEY=
INTERNAL_DS_TOKEN=
REDIS_PASSWORD=
CHROMA_HOST=
CHROMA_PORT=
CHROMA_COLLECTION=
LOG_LEVEL=
```

---

## 14. Entrenamiento y Actualización de Modelos IA

Actualmente el sistema utiliza:

- Claude Sonnet para extracción de intención.
- Modelo de embeddings preentrenado `paraphrase-multilingual-MiniLM-L12-v2`.

### Reentrenamiento de clasificadores auxiliares

```bash
cd ds/training

python prepare_dataset.py
python train_classifier.py
python evaluate_classifier.py
```

### Flujo recomendado

1. Exportar dataset etiquetado.
2. Dividir train/validation/test.
3. Entrenar modelo.
4. Ejecutar métricas.
5. Registrar versión.
6. Desplegar mediante CI/CD.

### Artefactos generados

```text
models/
├── classifier_v1.pkl
├── metrics.json
└── metadata.yaml
```

---

## 15. Reproducibilidad del Pipeline

Para reconstruir completamente el entorno:

```bash
git clone <repo>
cp .env.example .env
docker compose up -d

docker compose exec ds-api python pipeline/run_pipeline.py --all --rebuild-index
```

Validaciones posteriores:

```bash
curl http://localhost:8001/health
pytest ds/tests/
python eval/run_eval.py
```

---

## 16. Ejemplos Adicionales de Requests y Responses

### GET /search

Request

```http
GET /search?q=museos bilbao&limit=5
```

Response

```json
{
  "results": [
    {
      "id": "geu_001234",
      "name": "Museo Marítimo de Bilbao",
      "score": 0.91
    }
  ]
}
```

### GET /health

```json
{
  "status": "ok",
  "vector_store": "ok",
  "llm_api": "ok"
}
```

---

## 17. Limitaciones Técnicas

### Limitaciones actuales

- Dependencia de proveedores externos (Anthropic y Google Places).
- Calidad variable de datos procedentes de fuentes públicas.
- Escalabilidad no validada para más de 100.000 ubicaciones.
- Cobertura geográfica centrada en País Vasco.
- Reindexación principalmente batch.

### Riesgos

- Cambios de APIs externas.
- Incremento de costes de inferencia.
- Latencia dependiente del LLM.

---

## 18. Roadmap Técnico

### Corto plazo (0-3 meses)

- Observabilidad con Prometheus y Grafana.
- CI/CD automatizado.
- Cobertura de tests > 80%.
- Catálogo OpenAPI publicado.

### Medio plazo (3-6 meses)

- Búsqueda híbrida BM25 + vectorial.
- Feature store.
- Caché semántica.

### Largo plazo (6-12 meses)

- Multi-región.
- Recomendación personalizada por usuario.
- Fine-tuning especializado.
- Actualización continua de embeddings.
