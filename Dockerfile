# Chatbot de Eventos Culturales (Euskadi) — imagen del servicio Flask
# Ollama NO va dentro del contenedor: se consume desde el host vía OLLAMA_HOST.
FROM python:3.12-slim

# Evita .pyc y fuerza logs sin buffer (mejor para `docker compose logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Contexto de build = raíz del repo
WORKDIR /app

# Instalar dependencias primero para aprovechar la caché de capas
COPY models/Chatbot/requirements.txt /app/models/Chatbot/requirements.txt
RUN pip install --no-cache-dir -r /app/models/Chatbot/requirements.txt

# Copiar el resto del repo (respeta .dockerignore)
COPY . /app

# El entrypoint y el script LLM se ejecutan desde la carpeta del chatbot
WORKDIR /app/models/Chatbot

# Entrypoint configurable; por defecto app4.py
ENV APP_ENTRYPOINT=app4.py

# Flask escucha internamente en 5000 (ver app4.py)
EXPOSE 5000

# CMD recomendado: respeta APP_ENTRYPOINT con fallback a app4.py
CMD ["sh", "-c", "python ${APP_ENTRYPOINT:-app4.py}"]
