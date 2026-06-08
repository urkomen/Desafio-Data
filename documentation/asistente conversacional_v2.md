# Asistente conversacional de Eventos Culturales (Euskadi)

Asistente conversacional inteligente para descubrir eventos culturales del País Vasco usando procesamiento de lenguaje natural y datos abiertos.

---

**Última actualización**: Junio 2026

**Versión**: 5.0

## Historial de Versiones

| Versión     | Cambios                                   |
| ------------ | ----------------------------------------- |
| v1 (app.py)  | Versión inicial                          |
| v2 (app2.py) | Mejoras en formateo                       |
| v3 (app3.py) | Integración meteorología                |
| v4 (app4.py) | Optimizaciones de caché                  |
| v5 (app5.py) | **Versión actual - Refactorizado** |

---


## Tabla de Contenidos

- [Historial de Versiones](#historial-de-versiones)
- [Descripción General](#descripción-general)
- [Características Principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Estructura de Archivos](#estructura-de-archivos)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Configuración](#configuración)
- [Arquitectura Técnica Detallada](#arquitectura-técnica-detallada)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Módulos Detallados](#módulos-detallados)
- [Mejoras y Extensiones Futuras](#mejoras-y-extensiones-futuras)
- [Referencias](#referencias)
- [Stack Técnico](#stack-técnico)

## Descripción General

Sistema conversacional que permite a los usuarios consultar eventos culturales en lenguaje natural, con respuestas enriquecidas con:

- Información detallada de eventos (ubicación, fecha, precio, idioma)
- Datos meteorológicos en tiempo real (temperatura, precipitación)
- Filtrado automático mediante LLM (modelo de lenguaje local)
- Presentación en formato Markdown legible

## Características Principales:

- Búsqueda conversacional en lenguaje natural (español, euskera)
- Enriquecimiento automático con meteorología (Open-Meteo API)
- Procesamiento local con Ollama (sin dependencias cloud)
- Filtrado dinámico generado por LLM
- Caché local para optimización
- API REST con Flask
- Respuestas en Markdown formateadas

---

## Arquitectura

### Flujo de Procesamiento

```
Usuario: "Eventos gratis en Bilbao para hoy"
         ↓
    API Flask (app5.py)
         ↓
    API_LLM.py
         ↓
    1. Obtener eventos API Euskadi
    2. Obtener meteorología Open-Meteo
    3. Construir DataFrame Pandas
    4. Consultar LLM (Ollama)
         ↓
    LLM analiza consulta y genera código Python
    Ejemplo: df[(df['municipality'] == 'Bilbao') & (df['price'] == 0)]
         ↓
    5. Aplicar filtro
    6. Formatear resultados en Markdown
         ↓
    Respuesta al usuario con eventos, fechas, clima, precios
```

### Componentes del Sistema

| Componente                 | Descripción                                   | Responsable                                  |
| -------------------------- | ---------------------------------------------- | -------------------------------------------- |
| **app5.py**          | API REST Flask - enrutador de peticiones       | Recibe consultas, gestiona respuestas        |
| **API_LLM.py**       | Motor de procesamiento - orquestador principal | Coordina toda la lógica                     |
| **Ollama (Local)**   | Modelo de lenguaje                             | Genera filtros Python desde lenguaje natural |
| **API Euskadi**      | Fuente de eventos culturales                   | Proporciona datos de eventos                 |
| **Open-Meteo API**   | Servicio meteorológico                        | Enriquece con datos de clima                 |
| **Pandas DataFrame** | Estructura de datos en memoria                 | Almacena y filtra eventos                    |

### Capas del Sistema

```
┌─────────────────────────────────────┐
│    Capa de Presentación (Flask)     │  ← HTTP endpoints
├─────────────────────────────────────┤
│   Capa de Lógica (API_LLM.py)       │  ← Orquestación
├─────────────────────────────────────┤
│   Capa de Enriquecimiento           │  ← Meteorología
├─────────────────────────────────────┤
│   Capa de Datos (Pandas)            │  ← Filtering
├─────────────────────────────────────┤
│   Capa de Integración (APIs)        │  ← Euskadi, Open-Meteo
└─────────────────────────────────────┘
```

---

## Estructura de Archivos

```
models/Chatbot/
├── app5.py                 # API REST Flask (versión actual)
├── API_LLM.py              # Motor principal de procesamiento
├── requirements.txt        # Dependencias Python
├── README.md               # Este archivo
├── report.md               # Informe técnico detallado
└── old_versions/           # Versiones anteriores
    ├── API_LLM_original.py
    ├── API_LLM_original_v2.py
    ├── API_LLM_original_v3.py
    ├── API_LLM_original_v4.py
    ├── app.py (v1)
    ├── app2.py (v2)
    ├── app3.py (v3)
    └── app4.py (v4)
```

---

## Instalación y Ejecución

### Requisitos Previos

1. **Python 3.8+**
2. **Ollama** instalado y ejecutándose localmente
   - Descargar desde: https://ollama.ai
   - Modelo por defecto: `llama2` (puede cambiarse en el código)
3. **Conexión a internet** (para APIs de Euskadi y Open-Meteo)

### Instalación

```bash
# 1. Navegar a la carpeta
cd models/Chatbot

# 2. Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar Ollama (requisito previo)

En una terminal separada:

```bash
# Iniciar servidor Ollama (por defecto en puerto 11434)
ollama serve

# En otra terminal, descargar modelo si no lo tienes
ollama pull llama2
# O usar otro modelo:
# ollama pull mistral
# ollama pull neural-chat
```

### Ejecutar la API

```bash
python app5.py
```

**Salida esperada:**

```
Flask API running at http://127.0.0.1:5000/
```

---

## Ejemplos de Uso

### Endpoint Principal

```
GET http://localhost:5000/<consulta>
```

### Ejemplos de Consultas

#### 1. Eventos Gratis en Bilbao

```bash
curl "http://localhost:5000/Eventos%20gratis%20en%20Bilbao"
```

**Respuesta:** Lista de eventos gratuitos en Bilbao con fechas, clima, descripción.

#### 2. Eventos en Euskera esta Semana

```bash
curl "http://localhost:5000/Eventos%20en%20euskera%20para%20esta%20semana"
```

#### 3. Teatro en Donostia sin lluvia

```bash
curl "http://localhost:5000/Eventos%20de%20teatro%20en%20Donostia%20con%20baja%20lluvia"
```

#### 4. Eventos Infantiles Próximos

```bash
curl "http://localhost:5000/Planes%20para%20niños%20este%20mes"
```

### Respuesta Típica (Markdown)

```markdown
## Exposición: Guggenheim Bilbao
**Ubicación:** Bilbao  
**Fecha:** 15 de junio de 2026  
**Hora:** 10:00  
**Precio:** Gratis  
**Idioma:** Español  
**Clima:** 22°C, 40% humedad, viento 5 km/h

Descripción: Exposición temporal de arte moderno...

![Event image](https://...)

---
```

---

## Configuración

### Variables Clave en API_LLM.py

```python
# APIs de datos
EVENT_TYPES_API = "https://api.euskadi.eus/culture/events/v1.0/eventType"
UPCOMING_EVENTS_API = "https://api.euskadi.eus/culture/events/v1.0/events/upcoming?_elements=500"

# Caché local
CSV_PATH = "events_weather.csv"
CACHE_HOURS = 6  # Actualizar cada 6 horas

# Modelo Ollama
MODEL_NAME = "llama2"  # Cambiar por otro modelo si lo deseas
OLLAMA_HOST = "http://localhost:11434"
```

### Cambiar Modelo de LLM

En `API_LLM.py`, busca la línea donde se inicializa Ollama:

```python
response = ollama.generate(
    model="mistral",  # Cambiar aquí
    prompt=prompt,
    stream=False
)
```

**Modelos disponibles:**

- `llama2` - Buena relación calidad/velocidad
- `mistral` - Más rápido, bueno para filtros
- `neural-chat` - Especializado en conversación
- `orca-mini` - Ligero, rápido

---

## Arquitectura Técnica Detallada

### 1. Obtención de Datos

**Fuentes:**

```python
# Eventos culturales del País Vasco
https://api.euskadi.eus/culture/events/v1.0/events/upcoming

# Información meteorológica
https://api.open-meteo.com/v1/forecast
```

**Campos de Eventos:**

- `name_Es`, `name_Eu`, `name_Fr` (multilingüe)
- `startDate`, `endDate` (ISO 8601)
- `location.municipality` (municipio)
- `descriptions_Es` (descripción)
- `price` (tarifa, 0 = gratis)
- `eventType` (categoría)
- `latitude`, `longitude` (geolocalización)
- `images` (URLs de imágenes)

### 2. Enriquecimiento Meteorológico

Para cada evento con coordenadas, se consulta Open-Meteo:

```python
def get_weather_info(lat, lon):
    # Temperatura, humedad, velocidad del viento, precipitación
    # Predicción para el día del evento
    return {
        "temperature": 22.5,
        "humidity": 45,
        "wind_speed": 5.2,
        "precipitation_probability": 10
    }
```

### 3. Generación de Filtros con LLM

El LLM (via Ollama) interpreta la consulta natural y genera código Python:

**Entrada (consulta del usuario):**

```
"Eventos para niños sin lluvia en junio"
```

**Salida (código generado):**

```python
df[(df['category'].isin(['infantil', 'family'])) & 
   (df['precipitation_probability'] < 30) & 
   (df['startDate'].dt.month == 6)]
```

### 4. Ejecución de Filtros

Se evalúa el código generado de forma segura sobre el DataFrame.

### 5. Formateo de Salida

Conversion a Markdown:

```python
def format_event_md(event, lang="Es"):
    # Genera bloque Markdown con detalles, clima, imagen
    # Incluyendo nombre, ubicación, fecha, precio, descripción
```

---

## Performance

| Métrica                      | Valor      | Notas                            |
| ----------------------------- | ---------- | -------------------------------- |
| Tiempo respuesta (caché)     | ~2-3s      | Si datos en caché local         |
| Tiempo respuesta (sin caché) | ~8-12s     | Primera solicitud, descarga APIs |
| Eventos indexados             | ~500       | Configurables en API Euskadi     |
| Tamaño DataFrame             | ~50-100 MB | En memoria RAM                   |
| Latencia Ollama               | ~1-2s      | Depende del modelo               |

**Optimizaciones:**

- Caché CSV local (configurable cada 6 horas)
- Procesos paralelos para APIs
- Filtrado en DataFrame (optimizado con Pandas)
- LLM ejecutado localmente (sin latencia de red)

---

## Troubleshooting

### Error: "Connection refused" para Ollama

```
Error: Failed to connect to Ollama at http://localhost:11434
```

**Solución:**

```bash
# 1. Asegurate de que Ollama está ejecutándose
ollama serve

# 2. Verifica el puerto
lsof -i :11434

# 3. Intenta reiniciar Ollama
pkill ollama && ollama serve
```

### Error: "Model not found"

```
Error: model 'llama2' not found
```

**Solución:**

```bash
ollama pull llama2
# O cambiar a otro modelo disponible
ollama list
```

### API Euskadi: Sin respuesta o timeout

```
Error: requests.exceptions.Timeout
```

**Solución:**

- Verificar conexión a internet
- Intentar más tarde (API puede estar bajo mantenimiento)
- Usar datos en caché si está disponible

### Filtro incorrecto generado por LLM

Si el LLM genera código Python incorrecto:

1. Usar modelo diferente (más potente)
2. Mejorar el prompt en `API_LLM.py`
3. Añadir ejemplos de filtros en el contexto

---

## Módulos Detallados

### app5.py

API REST con Flask. Endpoints:

- `GET /` — Health check
- `GET /<consulta>` — Procesar consulta en lenguaje natural

```python
@app.route("/<path:question>")
def ask(question):
    # Llama API_LLM.py con la consulta
    # Devuelve Markdown con eventos filtrados
    output = run_script(question)
    return output, 200, {"Content-Type": "text/plain"}
```

### API_LLM.py

Orquestador principal. Funciones clave:

| Función                          | Propósito                               |
| --------------------------------- | ---------------------------------------- |
| `get_upcoming_events()`         | Obtiene eventos de API Euskadi           |
| `get_weather_info(lat, lon)`    | Consulta meteorología Open-Meteo        |
| `get_weather_for_events(df)`    | Enriquece DataFrame con clima            |
| `generate_filter(llm_output)`   | Convierte respuesta LLM a código Python |
| `apply_filter(df, filter_code)` | Ejecuta filtro sobre DataFrame           |
| `format_events_md(events)`      | Convierte a Markdown                     |

---

## Mejoras y Extensiones Futuras

### Corto Plazo

- [ ] Agregar autenticación/rate limiting
- [ ] Mejorar prompt para filtros más complejos
- [ ] Soporte para más idiomas
- [ ] Caché en base de datos (SQLite)

### Mediano Plazo

- [ ] Integración con recomendador de planes
- [ ] Historial de conversaciones por usuario
- [ ] Búsqueda por proximidad geográfica
- [ ] Alertas de eventos próximos

### Largo Plazo

- [ ] Fine-tuning de modelo LLM específico
- [ ] Interfaz conversacional multiturno
- [ ] Integración con sistemas de recomendación
- [ ] Análisis de preferencias del usuario

---

## Referencias

- **Documentación de Euskadi API**: https://www.euskadi.eus/contenidos/informacion/api_kultura_en/es_def/
- **Open-Meteo API**: https://open-meteo.com/
- **Ollama**: https://ollama.ai
- **Flask**: https://flask.palletsprojects.com/

---

## Stack Técnico

| Componente | Versión | Uso                |
| ---------- | -------- | ------------------ |
| Python     | 3.8+     | Runtime            |
| Flask      | 3.1.3    | Web framework      |
| Ollama     | 0.6.1+   | LLM local          |
| Requests   | 2.32.5   | Cliente HTTP       |
| Pandas     | 2.3.3    | Análisis de datos |
