# Desafío Data - Sistema Integral de Recomendación y Descubrimiento de Eventos

Este notebook documenta el resumen del proyecto completo de inteligencia artificial para la recomendación personalizada y el descubrimiento asistido de eventos culturales del País Vasco.

## 1. Estructura del Proyecto

```
Desafio-Data/
│
├── README.md                   # Documentación general
├── docker-compose.yml          # Orquestación de contenedores
├── Dockerfile                  # Imagen Docker del proyecto
│
├── models/                     # Sistemas de IA
│   ├── Recommender/            # Sistema de recomendación
│   │   ├── app.py              # API Flask del recomendador
│   │   ├── recommender.py      # Lógica de scoring y perfil
│   │   ├── config.py           # Configuración centralizada
│   │   ├── data_access.py      # Acceso a BD y embeddings
│   │   ├── location.py         # Detección de municipios
│   │   ├── requirements.txt
│       └── old_versions/       # Versión anterior
│   │
│   └── Guni/                   # Asistente conversacional
│       ├── app5.py             # API Flask del chatbot (versión actual)
│       ├── API_LLM.py          # Motor de procesamiento LLM
│       ├── requirements.txt
│       ├── report.md           # Informe técnico
│       └── old_versions/       # Versiones anteriores (v1–v4)
│
├── data/                       # Datos del proyecto
│   ├── descargas/              # Datasets CSV
│   │   ├── user_favorite_events.csv           # Eventos favoritos
│   │   ├── user_selected_recommendations.csv  # Historial de eventos con valoraciones
│   │   ├── users.csv                          # Usuarios
│   │   └── ...
│   ├── embeddings/              # Embeddings precalculados
│   │   ├── embeddings.npy       # Matriz de vectores (1024-dim)
│   │   └── embeddings_index.csv # Mapeo id → índice
│   └── eventos.db               # Base de datos SQLite
│
├── documentation/              # Documentación técnica
│   ├── guni.md                 # Memoria técnica del chatbot
│   ├── datos.md                # Memoria técnica de datos
│   └── recommender.md          # Memoria técnica del recomendador
│
├── notebooks/                  # Notebooks de análisis
│   ├── comparativa_embeddings.ipynb
│   ├── embedder_multilingual_e5.ipynb
│   ├── multilingual_large_embedding.ipynb
│   └── sql_eventos.ipynb
│
└── database/                   # Configuración de base de datos
```

## 2. Descripción del Proyecto

**Objetivo:** Construir una plataforma inteligente que transforme la manera en que personas y familias descubren eventos culturales en el País Vasco. En lugar de navegar por interminables listas o usar filtros manuales, el sistema actúa como un guía local experto.

**Problema que resuelve:** Conectar a los usuarios con eventos culturales que se ajusten perfectamente a su situación (perfil familiar, historial, preferencias, clima) de forma intuitiva y sin fricción.

**Clases de contenido:**

- Exposiciones y museos
- Conciertos y teatro
- Rutas de senderismo y actividades al aire libre
- Eventos infantiles y familiares

**Enfoque:** Dos sistemas de IA complementarios — un recomendador semántico personalizado y un asistente conversacional en lenguaje natural.

## 3. Experiencia Doble: Los Dos Sistemas

### Sistema 1: GUNI (Asistente Conversacional)

Asistente virtual con el que el usuario interactúa de forma natural, pensado para búsquedas rápidas e inmediatas.

**Ejemplo de uso:**

> *"Quiero un plan sin lluvia en Leioa"*
> *"Dime eventos gratis en Bilbao a partir de las 19:00"*

**Flujo:**

```
Usuario pregunta en lenguaje natural
        ↓
LLM (Ollama) analiza la consulta
Genera código Python de filtrado automático
        ↓
Descarga eventos desde API Euskadi
Enriquecimiento con datos meteorológicos (Open-Meteo)
Construcción de DataFrame Pandas
        ↓
Aplicación del filtro generado:
df[(df['price']==0) & (df['precipitation']<30) & (df['city']=='Bilbao')]
        ↓
Formateo de respuesta en Markdown
        ↓
Respuesta: Eventos filtrados con clima, precios e imágenes
```

### Sistema 2: El Recomendador Personalizado

Consejero a largo plazo que aprende de los gustos del usuario y su contexto familiar.

**Ejemplo de uso:**

> *"Museo en Bilbao para pasar un día en familia"*

**Flujo:**

```
Usuario busca con texto libre
        ↓
Análisis de consulta + lectura de perfil (edades, mascotas)
Revisión de historial (eventos visitados y valorados)
        ↓
Construcción de vector de perfil
(media ponderada de experiencias positivas)
        ↓
Cálculo de similitud semántica:
Score = α·sim(consulta) + β·sim(perfil) - penalización_reciente
        ↓
Aplicación de filtros duros (accesibilidad, precio, mascotas...)
        ↓
Ranking + boost para eventos promocionados
        ↓
Respuesta: Top 10 eventos personalizados
```

## 4. Los Datos

### Fuentes de Información:

1. **Catálogo Cultural:** API oficial de Euskadi con eventos clasificados y siempre actualizados
2. **Contexto Meteorológico:** Integración con Open-Meteo para condiciones climáticas en tiempo real
3. **Perfiles y Experiencias:** Historial de usuarios, composición familiar y valoraciones previas

### Base de Datos (`eventos.db`):

- `events_table` — Catálogo de eventos con metadatos completos
- `users_table` — Usuarios registrados
- `families_table` — Perfiles familiares (edades, mascotas, preferencias)
- `user_events_history` — Historial de asistencia y valoraciones

### Embeddings Precalculados:

- **Modelo:** `intfloat/multilingual-e5-large`
- **Dimensión:** 1024 vectores por evento
- **Similitud:** Coseno (producto escalar sobre vectores normalizados)
- **Archivos:** `embeddings/embeddings.npy` + `embeddings/embeddings_index.csv`

### Estadísticas:

| Métrica                 | Valor                              |
| ------------------------ | ---------------------------------- |
| Eventos Indexados        | ~500                               |
| Dimensión de Embeddings | 1024                               |
| Idiomas Soportados       | 3 (ES, EU, FR)                     |
| APIs Integradas          | 3 (Euskadi, Open-Meteo, Ollama)    |
| Tiempo de Respuesta      | 2-3s (caché) / 8-12s (sin caché) |

## 5. Evolución del Producto: Fases de Desarrollo

### Fase 1 — MVP (Día 1): El Producto Mínimo Viable

- Guni recibe input y devuelve eventos en lista plana
- Recomendador con cruces de datos simples
- Datos ficticios en ficheros CSV
- Objetivo: conectar las piezas y demostrar que la idea funciona

### Fase 2 — Mejoras de Consultas (Días 2-4)

- Guni devuelve información visualmente mejorada (v2)
- Integración del clima en tiempo real (v3)
- Vectorización de planes y usuarios con embeddings semánticos
- Sustitución de datos ficticios por datos reales de la API Euskadi

### Fase 3 — Consultas Personalizadas (Días 4-5)

- Guni optimizado para responder mucho más rápido (v4 → v5)
- La IA genera filtros Python directamente desde lenguaje natural
- Incorporación del `score_final` con boost promocional en el recomendador
- Creación de tablas relacionales y consulta desde BD
- Penalización temporal para no repetir eventos visitados recientemente

### Fase 4 — Conexión entre Modelos (Futuro)

- Conectar Guni al motor recomendador para respuestas más sofisticadas
- Similitud entre usuarios (filtrado colaborativo)
- Clusterización de planes y modelo SVC para clasificar nuevos eventos
- Limpieza y mejora de calidad de datos más exhaustiva

## 6. Módulos Principales

### 6.1 Recomendador (`models/Recommender/`)

```python
# Uso principal del recomendador
POST /recomendar
{
    "user_id": 123,
    "query": "Museo en Bilbao para pasar el día en familia",
    "filters": {"precio_max": 10, "mascotas": True}
}
```

- **`app.py`** — API Flask, punto de entrada REST
- **`recommender.py`** — Lógica de scoring, ponderación y perfil
- **`config.py`** — Configuración centralizada (rutas, hiperparámetros, pesos α/β)
- **`data_access.py`** — Acceso a la BD SQLite y carga de embeddings `.npy`
- **`location.py`** — Detección y normalización de municipios

### 6.2 Asistente Conversacional (`models/Guni/`)

```python
# Uso principal del chatbot
POST /ask
{
    "message": "Eventos gratis para niños esta semana sin lluvia"
}
```

- **`app5.py`** — API Flask, versión de producción actual (v5)
- **`API_LLM.py`** — Motor de procesamiento: interpreta la consulta y genera filtros
- **`old_versions/`** — Historial de versiones anteriores (v1–v4) para referencia

### 6.3 Notebooks de Análisis (`notebooks/`)

| Notebook                               | Propósito                                      |
| -------------------------------------- | ----------------------------------------------- |
| `embedder_multilingual_e5.ipynb`     | Generación de embeddings con el modelo E5      |
| `comparativa_embeddings.ipynb`       | Análisis comparativo de modelos de embeddings  |
| `multilingual_large_embedding.ipynb` | Experimentos con el modelo large                |
| `sql_eventos.ipynb`                  | Exploración y consultas sobre la base de datos |

## 7. Arquitectura Técnica

```
┌─────────────────────────────────────────────────────────────┐
│                    Capa de Presentación                     │
│              (Web, Mobile Apps, API Clients)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    APIs REST (Flask)                        │
│   /recomendar (Recomendador)  /ask (Chatbot)                │
└────────────┬──────────────────────────┬─────────────────────┘
             │                          │
    ┌────────▼──────────┐    ┌─────────▼─────────────┐
    │   Recomendador    │    │   Asistente (Ollama)  │
    │                   │    │                       │
    │ • Scoring         │    │ • LLM Generation      │
    │ • Similarity      │    │ • Natural Language    │
    │ • Filtering       │    │ • Filtering Logic     │
    └────────┬──────────┘    └─────────┬─────────────┘
             │                         │
    ┌────────▼──────────┐    ┌─────────▼─────────────┐
    │  Embeddings       │    │   External APIs       │
    │  (1024-dim)       │    │                       │
    │  Normalized       │    │ • Euskadi Events      │
    │  Cosine Sim       │    │ • Open-Meteo Weather  │
    └────────┬──────────┘    └─────────┬─────────────┘
             │                         │
    ┌────────▼──────────────────────────▼─────────────┐
    │              SQLite Database                    │
    │  • events_table                                 │
    │  • users_table                                  │
    │  • families_table                               │
    │  • user_events_history                          │
    └─────────────────────────────────────────────────┘
```

### Tecnologías Principales

| Capa                   | Tecnología                        |
| ---------------------- | ---------------------------------- |
| Framework API          | Flask (REST)                       |
| LLM local              | Ollama (sin dependencias cloud)    |
| Embeddings             | `intfloat/multilingual-e5-large` |
| Base de datos          | SQLite                             |
| Procesamiento de datos | Pandas                             |
| Contenedorización     | Docker + Docker Compose            |
| API de eventos         | Euskadi Cultural Events API        |
| API del clima          | Open-Meteo                         |

## 8. Cómo Usar el Sistema

### Instalación con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/urkomen/Desafio-Data.git
cd Desafio-Data

# 2. Compilar y ejecutar con Docker Compose
docker-compose up -d

# Los servicios estarán disponibles en:
# - Recomendador: http://localhost:5000
# - Asistente conversacional: http://localhost:5001
```

### Instalación Local

```bash
# Recomendador
cd models/Recommender
pip install -r requirements.txt
python app.py

# Asistente conversacional (requiere Ollama)
curl https://ollama.ai/install.sh | sh
ollama serve

cd models/Guni
pip install -r requirements.txt
python app5.py
```

### Requisitos

- Python 3.8+
- Docker & Docker Compose (recomendado)
- Ollama (para el Asistente)
- RAM mínima: 4 GB | Recomendada: 16 GB
- Disco: 5 GB mínimo / 20 GB recomendado
- Internet para APIs externas (Euskadi, Open-Meteo)

## 9. Ejemplo de Flujo Completo de Usuario

### Día 1: Usuario Nuevo

1. Usuario se registra y completa su perfil familiar (2 niños pequeños, 1 perro)
2. Usa **Guni** para buscar: *"Planes para familias con niños pequeños"*
3. Guni filtra eventos al aire libre, con cambiadores y que admitan mascotas
4. Recibe recomendaciones inmediatas (sin historial: 90% consulta + 10% perfil)

### Día 7: Usuario con Historial

1. Usuario ha visitado 3 eventos (2 eventos con 5⭐, 1 evento con 4⭐)
2. Usa el **Recomendador**: *"Busco algo parecido a lo que me encantó"*
3. Sistema detecta el patrón: *"Le encantaron museos y exposiciones"*
4. Ponderación adaptativa: 50% consulta + 50% perfil histórico
5. Penalización automática de eventos visitados recientemente
6. Recibe recomendaciones altamente personalizadas

## 10. Conclusiones y Próximos Pasos

### Hallazgos Principales:

- El enfoque de embeddings semánticos multilingües (`multilingual-e5-large`) permite capturar la intención del usuario con alta precisión independientemente del idioma
- La combinación del recomendador semántico + asistente conversacional cubre casos de uso complementarios: descubrimiento rápido vs. personalización profunda
- El uso de LLM local (Ollama) elimina dependencias cloud y garantiza la privacidad de las consultas
- La ponderación adaptativa α/β según el historial del usuario mejora significativamente la relevancia de las recomendaciones

### Sistema Listo para Usar:

- `models/Guni/app5.py` — Asistente en producción (v5)
- `models/Recommender/app.py` — Recomendador en producción
- Pipeline de embeddings precalculados y actualizables
- Dockerizado para despliegue inmediato

### Mejoras Futuras:

- Conectar Guni al motor recomendador para respuestas enriquecidas
- Implementar similitud entre usuarios (filtrado colaborativo)
- Clusterización de planes + modelo SVC para clasificar nuevos eventos automáticamente
- Mejora de la calidad de datos con pipeline de limpieza más exhaustivo
- Testing A/B entre versiones del recomendador

## 11. Referencias

### Documentación Interna

- **Memoria técnica del Chatbot:** `documentation/guni.md`
- **Memoria técnica del Recomendador:** `documentation/recommender.md`
- **Memoria técnica de Datos:** `documentation/datos.md`

### Frameworks & Librerías

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Ollama](https://ollama.ai)
- [Pandas](https://pandas.pydata.org/)

### APIs Externas

- [Euskadi Cultural Events API](https://www.euskadi.eus/contenidos/informacion/api_kultura_en/es_def/)
- [Open-Meteo Weather API](https://open-meteo.com/)

### Papers & Recursos de IA

- Embeddings Multilingües: [Multilingual E5](https://arxiv.org/abs/2402.05672)
- Sistemas de Recomendación: [Collaborative Filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)

### Contribuidores

- Urko Menendez
- Ruben Novoa
- Danillo Barros de Souza
- Oscar Fernandez
