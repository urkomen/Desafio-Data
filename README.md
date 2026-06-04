## 🔎 Uso

### Desde el navegador

Ejemplo:

http://127.0.0.1:5000/Eventos%20gratuitos%20en%20Bilbao

### Desde la terminal con cURL

Ejemplo:

```bash
curl "http://127.0.0.1:5000/Eventos%20en%20euskera"
```

## 🧠 Funcionamiento interno

1. Flask recibe la petición.
2. Ejecuta `API_LLM.py` mediante `subprocess`.
3. Se consultan APIs externas:
   - Eventos culturales (Euskadi)
   - Meteorología (Open-Meteo)
4. Se construye un DataFrame con Pandas.
5. El LLM (Ollama) genera un filtro Python.
6. Se ejecuta el filtro con `eval()`.
7. Se formatean los resultados en Markdown.

## 🌤️ APIs utilizadas

- Euskadi Open Data (eventos culturales)
- Open-Meteo (meteorología)

## 🤖 Modelo LLM

Modelo utilizado: `qwen2.5-coder`

Motor: `Ollama`

Parámetros:

```python
temperature = 0.1
top_p = 0.2
```

El modelo solo genera código Python para filtrar el DataFrame.

## 📊 Características

- Chatbot basado en datos reales
- Sin RAG ni embeddings
- Arquitectura ligera
- Ejecución local completa
- Respuestas en Markdown enriquecido
- Integración con clima en tiempo real

## ⚠️ Limitaciones

- Uso de `eval()` para ejecutar código generado por el LLM
- Dependencia de APIs externas
- Pensado para entorno controlado (no producción)

## 🛠️ Mejoras futuras

- Sustituir `eval()` por ejecución segura
- Añadir frontend web
- Dockerización
- Sistema de caché avanzado
- Autenticación API
- Tests automáticos
