# Informe Técnico del Proyecto Chatbot de Eventos Culturales del País Vasco

## 1. Introducción

Este proyecto implementa un chatbot especializado en la búsqueda y recomendación de eventos culturales del País Vasco utilizando datos abiertos proporcionados por la API de Euskadi.

El sistema combina:

* Obtención de eventos culturales desde APIs públicas.
* Enriquecimiento de los eventos con información meteorológica.
* Uso de un modelo de lenguaje (LLM) ejecutado localmente mediante Ollama.
* Generación dinámica de filtros sobre un conjunto de datos estructurado.
* Presentación de resultados en formato Markdown.
* Exposición del servicio mediante una API REST desarrollada con Flask.

---

# 2. Arquitectura General

```text
Usuario
   │
   ▼
API Flask (app.py)
   │
   ▼
API_LLM.py
   │
   ├── Obtención de eventos (API Euskadi)
   │
   ├── Obtención de meteorología (Open-Meteo)
   │
   ├── Construcción DataFrame Pandas
   │
   ├── Caché CSV local
   │
   ├── Consulta al LLM (Ollama)
   │
   ├── Generación de filtro Python
   │
   ├── Aplicación del filtro
   │
   └── Generación Markdown
   │
   ▼
Respuesta al usuario
```

---

# 3. Objetivos del Proyecto

El objetivo principal es permitir que un usuario consulte eventos culturales utilizando lenguaje natural.

Ejemplos:

* Eventos gratuitos en Bilbao.
* Eventos en euskera.
* Eventos para esta tarde.
* Eventos con baja probabilidad de lluvia.
* Eventos de teatro durante el mes de mayo.

El sistema traduce automáticamente estas consultas en filtros sobre un DataFrame de Pandas.

---

# 4. Fuentes de Datos

## API de Eventos Culturales

Se utilizan los siguientes endpoints:

```python
EVENT_TYPES_API
```

Obtiene los tipos de eventos disponibles.

```python
UPCOMING_EVENTS_API
```

Obtiene los eventos próximos.

Información disponible:

* Nombre
* Municipio
* Lugar
* Fechas
* Descripción
* Idioma
* Precio
* Tipo de evento
* Coordenadas geográficas
* Imágenes
* Horarios

---

## API Meteorológica

Proveedor:

Open-Meteo

Información obtenida:

* Temperatura
* Humedad
* Velocidad del viento
* Probabilidad de precipitación

La información se calcula para las siguientes 6 horas.

---

# 5. Descripción de Funciones

## get_event_types()

### Objetivo

Obtiene los tipos de eventos disponibles desde la API de Euskadi.

### Entrada

Ninguna.

### Salida

```python
dict
```

### Funcionamiento

1. Realiza una petición HTTP GET.
2. Convierte la respuesta a JSON.
3. Devuelve el resultado.

---

## get_upcoming_events()

### Objetivo

Obtiene el listado de eventos próximos.

### Entrada

Ninguna.

### Salida

```python
dict
```

### Funcionamiento

1. Consulta la API de Euskadi.
2. Recupera los eventos.
3. Devuelve el contenido en formato JSON.

---

## clean_html(text)

### Objetivo

Eliminar etiquetas HTML de los textos recibidos.

### Entrada

```python
str
```

### Salida

```python
str
```

### Funcionamiento

1. Convierte entidades HTML.
2. Elimina etiquetas HTML mediante expresiones regulares.
3. Devuelve texto limpio.

---

## fmt_date(date_str)

### Objetivo

Formatear fechas para su visualización.

### Entrada

```python
str
```

### Salida

```python
str
```

### Funcionamiento

1. Convierte fechas ISO.
2. Formatea la fecha.
3. Devuelve una representación amigable para el usuario.

---

## is_valid(value)

### Objetivo

Validar si un campo contiene información útil.

### Entrada

```python
Any
```

### Salida

```python
bool
```

### Criterios

Considera inválidos:

* None
* NaN
* Strings vacíos

---

## extract_image(event)

### Objetivo

Extraer la imagen principal de un evento.

### Entrada

```python
dict
```

### Salida

Markdown con la imagen.

Ejemplo:

```markdown
![Evento](url)
```

### Funcionamiento

1. Obtiene la lista de imágenes.
2. Selecciona la primera.
3. Construye el Markdown correspondiente.

---

## get_weather_info(lat, lon)

### Objetivo

Consultar información meteorológica asociada a una localización.

### Entrada

```python
lat
lon
```

### Salida

```python
dict
```

### Campos retornados

```python
temperature
humidity
wind_speed
precipitation_probability
time
last_updated
```

### Funcionamiento

1. Consulta Open-Meteo.
2. Calcula una predicción para las próximas 6 horas.
3. Devuelve las variables meteorológicas relevantes.

---

## format_event_md(event)

### Objetivo

Transformar un evento en una ficha Markdown enriquecida.

### Información incluida

* Nombre
* Fecha
* Horario
* Municipio
* Lugar
* Tipo de evento
* Idioma
* Precio
* Enlace web
* Imagen
* Mapa
* Meteorología
* Descripción

### Salida

```markdown
## Evento

Fecha
Lugar
Precio
Descripción
...
```

---

## format_events_md(events)

### Objetivo

Generar una salida Markdown para múltiples eventos.

### Entrada

```python
list[dict]
```

### Salida

```markdown
Evento 1

Evento 2

Evento 3
```

---

## is_cache_valid(path, hours)

### Objetivo

Determinar si el fichero CSV de caché sigue siendo válido.

### Entrada

```python
path
hours
```

### Salida

```python
bool
```

### Funcionamiento

1. Comprueba la existencia del archivo.
2. Evalúa la antigüedad.
3. Determina si debe reutilizarse.

---

## build_dataframe()

### Objetivo

Construir el DataFrame principal utilizado por el chatbot.

### Salida

```python
pandas.DataFrame
```

### Proceso

1. Descarga eventos.
2. Extrae municipios.
3. Obtiene meteorología para cada municipio.
4. Fusiona ambas fuentes.
5. Devuelve el DataFrame final.

### Variables añadidas

```python
temperature
humidity
wind_speed
precipitation_probability
time
last_updated
```

---

## ask_model(question)

### Objetivo

Consultar el modelo de lenguaje local.

### Entrada

```python
str
```

### Salida

Código Python generado por el modelo.

### Funcionamiento

1. Construye un prompt con el contexto del DataFrame.
2. Envía la consulta a Ollama.
3. Obtiene código Python como respuesta.

Ejemplo:

Pregunta:

```text
Eventos gratuitos en Bilbao
```

Respuesta generada:

```python
I[(I.municipalityEs=="Bilbao") & (I.priceEs=="Gratis")]
```

---

## make_assignment(llm_output)

### Objetivo

Extraer el bloque Python generado por el modelo.

### Entrada

```python
str
```

### Salida

```python
str
```

### Funcionamiento

1. Busca bloques ```python.
2. Extrae la expresión.
3. Devuelve el código limpio.

---

## apply_filter(expr)

### Objetivo

Ejecutar el filtro generado por el modelo.

### Entrada

```python
str
```

### Salida

```python
DataFrame
```

### Funcionamiento

1. Ejecuta la expresión mediante eval().
2. Devuelve el subconjunto filtrado.

---

# 6. Caché de Datos

El sistema implementa una caché local.

Archivo:

```text
events_weather.csv
```

Duración:

```python
CACHE_HOURS = 6
```

Ventajas:

* Reduce llamadas a APIs externas.
* Disminuye tiempos de respuesta.
* Reduce consumo de red.

---

# 7. Uso del Modelo de Lenguaje

Modelo utilizado:

```text
qwen2.5-coder:latest
```

Ejecutado mediante:

```text
Ollama
```

El modelo no genera texto libre.

Su única responsabilidad es generar expresiones Python válidas que filtren el DataFrame.

Esto permite:

* Mayor control.
* Menor alucinación.
* Consultas reproducibles.
* Mejor rendimiento.

---

# 8. API REST

Archivo:

```python
app.py
```

Framework:

```python
Flask
```

---

## Endpoint de Estado

```http
GET /
```

Respuesta:

```json
{
  "status": "ok"
}
```

---

## Endpoint de Consulta

```http
GET /<pregunta>
```

Ejemplo:

```http
GET /Eventos gratuitos en Bilbao
```

Proceso:

1. Flask recibe la petición.
2. Ejecuta API_LLM.py mediante subprocess.
3. Obtiene la respuesta Markdown.
4. Devuelve el resultado al cliente.

---

# 9. Fortalezas del Sistema

* Utiliza datos abiertos oficiales.
* Funciona completamente en local.
* No depende de servicios LLM externos.
* Incluye enriquecimiento meteorológico.
* Genera respuestas visuales en Markdown.
* Arquitectura sencilla y fácil de desplegar.

---

# 10. Riesgos y Limitaciones

## Uso de eval()

Actualmente se ejecuta:

```python
eval(expr)
```

Esto supone un riesgo de seguridad potencial.

Se recomienda:

* Validar expresiones.
* Utilizar un parser seguro.
* Implementar una lista blanca de operaciones.

---

## Redefinición de funciones

El archivo contiene múltiples definiciones repetidas de:

```python
format_event_md()
extract_image()
fmt_date()
```

Solo la última definición es utilizada.

Se recomienda consolidarlas.

---

## Variables Globales

El DataFrame principal:

```python
I
```

se utiliza globalmente.

Se recomienda encapsular la lógica en clases o módulos especializados.

---

# 11. Mejoras Futuras

* Incorporar búsqueda semántica.
* Añadir ranking de relevancia.
* Exponer API OpenAPI/Swagger.
* Implementar autenticación.
* Sustituir eval() por ejecución segura.
* Añadir tests automáticos.
* Dockerización completa.
* Internacionalización completa ES/EU/EN/FR.
* Geolocalización automática del usuario.
* Recomendaciones personalizadas.

---

# 12. Conclusión

Se ha desarrollado un chatbot especializado en eventos culturales capaz de transformar consultas en lenguaje natural en filtros ejecutables sobre un conjunto de datos enriquecido con información meteorológica.

La solución combina técnicas de recuperación de información, procesamiento de datos con Pandas, modelos de lenguaje ejecutados localmente mediante Ollama y una API REST ligera basada en Flask.

El resultado es una plataforma capaz de proporcionar recomendaciones de eventos contextualizadas, actualizadas y enriquecidas con información práctica para facilitar la toma de decisiones por parte del usuario.
