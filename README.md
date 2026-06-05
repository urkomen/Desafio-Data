# Chatbot de Eventos Culturales (Euskadi)

## 📌 Descripción

Este proyecto es un chatbot minimalista que permite consultar eventos culturales del País Vasco utilizando lenguaje natural.

El sistema:

- Consume APIs públicas de eventos culturales del Gobierno Vasco.
- Enriquece los eventos con información meteorológica mediante Open-Meteo.
- Construye un DataFrame con Pandas como base de datos en memoria.
- Utiliza un LLM local (Ollama) para transformar preguntas en filtros Python.
- Ejecuta dichos filtros sobre el DataFrame.
- Devuelve la respuesta en formato Markdown.
- Expone el sistema mediante una API REST con Flask.

---

## ⚙️ Arquitectura

Usuario  
→ Flask (app.py)  
→ API_LLM.py  
→ APIs externas + Pandas + Ollama  
→ LLM genera filtros Python  
→ Evaluación sobre DataFrame  
→ Respuesta Markdown  

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone <repo_url>
cd <project_folder>
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Ollama

https://ollama.com

Descargar modelo:

```bash
ollama pull qwen2.5-coder
```

---

## 📄 Dependencias

flask==3.1.3  
ollama==0.6.1  
requests==2.32.5  
pandas==2.3.3  

---

## 🚀 Ejecución

### Iniciar servidor Flask

```bash
python3 app.py
```

Servidor:

http://127.0.0.1:5000

---

## 🔎 Uso

### Navegador

http://127.0.0.1:5000/Eventos%20gratuitos%20en%20Bilbao

### cURL

```bash
curl "http://127.0.0.1:5000/Eventos%20en%20euskera"
```

---

## 🧠 Funcionamiento interno

1. Flask recibe la petición.
2. Ejecuta API_LLM.py.
3. Consulta APIs externas.
4. Obtiene eventos culturales.
5. Obtiene datos meteorológicos.
6. Construye DataFrame con Pandas.
7. LLM genera filtro Python.
8. Eval ejecuta filtro.
9. Respuesta en Markdown.

---

## 🌤️ APIs utilizadas

- Euskadi Open Data
- Open-Meteo

---

## 🤖 Modelo LLM

qwen2.5-coder via Ollama

temperature = 0.1  
top_p = 0.2  

Ejemplo:

df[(df["municipality"]=="Bilbao") & (df["price"]==0)]

---

## 📊 Características

- Chatbot basado en datos reales
- APIs públicas
- Ejecución local
- Ollama LLM
- Markdown responses
- Integración clima

---

## ⚠️ Limitaciones

- Uso de eval()
- Dependencia APIs externas
- No producción

---

## 🛠️ Mejoras futuras

- Sustituir eval
- Frontend
- Docker
- Caché
- Auth
- Tests
