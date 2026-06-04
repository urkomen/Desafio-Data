**Chatbot de Eventos Culturales (Euskadi)**  
**📌 Descripción**  
Este proyecto es un chatbot minimalista que permite consultar eventos culturales del País Vasco utilizando lenguaje natural.  
El sistema:  
- Consume APIs públicas de eventos culturales del Gobierno Vasco.  
- Enriquese los eventos con información meteorológica (Open-Meteo).  
- Construye un DataFrame con Pandas como base de datos en memoria.  
- Utiliza un modelo LLM local (Ollama) para transformar preguntas en filtros Python.  
- Ejecuta esos filtros para obtener resultados.  
- Devuelve la respuesta en formato Markdown.  
- Expone el sistema mediante una API REST con Flask.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCUrfDqrYGVDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHCQGBEuErVgAAAAASUVORK5CYII=)  
**⚙️ Arquitectura**  
Usuario  
   
 → Flask (app.py)  
   
 → API_LLM.py  
   
 → APIs externas + Pandas + Ollama  
   
 → LLM genera filtros Python  
   
 → Evaluación sobre DataFrame  
   
 → Respuesta Markdown  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhYMMAKlD4OzrxgQU2QtIq6DIzR3UFAMBf3Gu1VefXEwAAXtsfSqADWz4G/HUAAAAASUVORK5CYII=)  
**📦 Instalación**  
**1. Clonar el repositorio**  
git clone <repo_url>  
 cd <project_folder>  
   
**2. Crear entorno virtual (recomendado)**  
python3 -m venv venv  
 source venv/bin/activate  
   
**3. Instalar dependencias**  
pip install -r requirements.txt  
   
**4. Instalar Ollama**  
[https://ollama.com](https://ollama.com "https://ollama.com")  
Descargar el modelo:  
ollama pull qwen2.5-coder  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCUrfD6LYGNDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHDAF/orRG+cAAAAASUVORK5CYII=)  
**📄 Dependencias**  
flask==3.1.3  
   
 ollama==0.6.1  
   
 requests==2.32.5  
   
 pandas==2.3.3  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUfyNTCi9VwgEA3sWGAjJK2CbjNzVGcAAPzFtapV7V9PAAB47X4AEW4ELQDBN+AAAAAASUVORK5CYII=)  
**🚀 Ejecución**  
**Iniciar servidor Flask**  
python3 app.py  
   
Servidor:  
   
 http://127.0.0.1:5000  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGhrOTvaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhYQEO+64Y8AAAAAASUVORK5CYII=)  
**🔎 Uso**  
Ejemplo:  
   
 http://127.0.0.1:5000/Eventos gratuitos en Bilbao  
Con curl:  
   
 curl "http://127.0.0.1:5000/Eventos en euskera"  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSeYxZw/lieLGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fGBdgoVMwYAAAAAElFTkSuQmCC)  
**🧠 Funcionamiento interno**  
1. Flask recibe la petición.  
2. Ejecuta API_LLM.py mediante subprocess.  
3. Se consultan APIs externas:  
  - Eventos culturales (Euskadi)  
  - Meteorología (Open-Meteo)  
4. Se construye un DataFrame con Pandas.  
5. El LLM (Ollama) genera un filtro Python.  
6. Se ejecuta el filtro con eval().  
7. Se formatean los resultados en Markdown.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAALUlEQVR4nO3OQQ0AIAwEsAMlSJ0UrOFkGngRklZBR1WtJDsAAPzizNcDAADuNcKwAyU+nb+5AAAAAElFTkSuQmCC)  
**🌤️ APIs utilizadas**  
- Euskadi Open Data (eventos culturales)  
- Open-Meteo (meteorología)  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OQQmAUBBAwSeILbyYdDP8jAaxgjcRZhLMNjNntQIA4C/uvTqq6+sJAADvPS2NA0FrXqf/AAAAAElFTkSuQmCC)  
**🤖 Modelo LLM**  
Modelo utilizado: qwen2.5-coder  
   
 Motor: Ollama  
   
 Parámetros:  
   
 temperature = 0.1  
   
 top_p = 0.2  
El modelo SOLO genera código Python para filtrar el DataFrame.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBACP6MMH6NpGACyywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AL+6BElk4wV6AAAAAElFTkSuQmCC)  
**📊 Características**  
- Chatbot basado en datos reales  
- Sin RAG ni embeddings  
- Arquitectura ligera  
- Ejecución local completa  
- Respuestas en Markdown enriquecido  
- Integración con clima en tiempo real  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFgpQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTRBeEgNK9YAAAAAElFTkSuQmCC)  
**⚠️ Limitaciones**  
- Uso de eval() para ejecutar código generado por el LLM  
- Dependencia de APIs externas  
- Pensado para entorno controlado (no producción)  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCUrfDqrYGVDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHCQGBEuErVgAAAAASUVORK5CYII=)  
**🛠️ Mejoras futuras**  
- Sustituir eval() por ejecución segura  
- Añadir frontend web  
- Dockerización  
- Sistema de caché avanzado  
- Autenticación API  
- Tests automáticos  

---

## 🐳 Docker

El chatbot Flask (`models/Chatbot/app4.py`) se puede ejecutar en un contenedor para
consumirlo desde otros servicios (p. ej. el backend Express de DESAFIO-26).

**Importante:** Ollama **NO** corre dentro del contenedor. El contenedor llama al
Ollama instalado en el **host** mediante la variable `OLLAMA_HOST`.

### Requisitos previos

- Docker + Docker Compose.
- Ollama corriendo en el host con el modelo descargado:
  ```bash
  ollama pull qwen2.5-coder
  ```
  Asegúrate de que Ollama está escuchando en `11434`. En Docker Desktop (Mac/Windows)
  el contenedor lo alcanza vía `host.docker.internal`. Si la conexión falla, arranca
  Ollama escuchando en todas las interfaces:
  ```bash
  OLLAMA_HOST=0.0.0.0:11434 ollama serve
  ```

### Configuración

| Parámetro            | Valor                                   |
|----------------------|-----------------------------------------|
| Imagen base          | `python:3.12-slim`                      |
| Contexto de build    | raíz del repo                           |
| `WORKDIR`            | `/app/models/Chatbot`                   |
| Entrypoint (default) | `app4.py` (configurable: `APP_ENTRYPOINT`) |
| Puerto interno Flask | `5000`                                  |
| Puerto en el host    | `5001` (`5001:5000`)                    |
| Ollama del host      | `OLLAMA_HOST=http://host.docker.internal:11434` |

### Uso

```bash
# Construir
docker compose build

# Arrancar en segundo plano
docker compose up -d

# Estado
docker compose ps

# Health-check (JSON inmediato)
curl http://localhost:5001/

# Consulta en lenguaje natural (lanza Ollama + APIs externas; puede tardar)
curl "http://localhost:5001/Plan%20gratis%20para%20hoy%20en%20Bilbao"

# Logs
docker compose logs --tail=80

# Parar
docker compose down
```

> La primera consulta construye un DataFrame consultando APIs externas (Euskadi +
> Open-Meteo) y luego invoca el LLM, por lo que puede tardar varios segundos.

### Endpoints expuestos

- `GET /` → estado del servicio (JSON).
- `GET /<pregunta>` → respuesta en Markdown a la pregunta en lenguaje natural.

### Cambiar el entrypoint (opcional)

```bash
APP_ENTRYPOINT=app3.py docker compose up
```

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OUQmAQBBAwSdcjsu6HYxoDsEK/okwk2COmdnVGQAAf3GtalX76wkAAK/dDxFWBDkFf6+SAAAAAElFTkSuQmCC)  
