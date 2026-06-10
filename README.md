# Desafío Data - Sistema Integral de Recomendación y Descubrimiento de Eventos

**Plataforma inteligente para la recomendación personalizada y descubrimiento asistido de eventos culturales del País Vasco.**

---

## Tabla de Contenidos

- [Descripción General](#-Descripción-General)
- [Características Principales](#-Características-Principales)
- [Estructura del Proyecto](#-Estructura-del-Proyecto)
- [Componentes del Sistema](#-Componentes-del-Sistema)
- [Instalación Rápida](#-Instalación-Rápida)
- [Guía de Uso](#-Guía-de-Uso)
- [Ejemplos Prácticos](#-Ejemplos-Prácticos)
- [Arquitectura Técnica](#-Arquitectura-Técnica)
- [Requisitos](#-Requisitos)
- [Documentación Completa](#-Documentación-Completa)

---

## Descripción General

Este proyecto integra dos sistemas complementarios de inteligencia artificial para mejorar la experiencia de descubrimiento de eventos culturales y planes familiares:

### **Sistema 1: Recomendador Semántico**

Proporciona recomendaciones altamente personalizadas basadas en:

- Búsqueda específica del usuario
- Perfil familiar (edades, mascotas)
- Filtros de accesibilidad y preferencias
- Historial de eventos visitados del usuario y lista de eventos favoritos

### **Sistema 2: Asistente Conversacional**

Asistente que permite:

- Búsqueda en lenguaje natural
- Filtrado automático mediante IA
- Enriquecimiento con datos meteorológicos
- Respuestas formateadas e inmediatas

---

## Características Principales

### Inteligencia Artificial

- Embeddings multilingües semánticos (`intfloat/multilingual-e5-large`)
- Modelo de lenguaje local (Ollama - sin dependencias cloud)
- Ponderación adaptativa según perfil del usuario
- Generación automática de filtros desde lenguaje natural

### Datos Enriquecidos

- Integración con APIs públicas (Euskadi cultural events)
- Datos meteorológicos en tiempo real (Open-Meteo)
- Soporte multilingüe (Español, Euskera, Francés)
- Información detallada de eventos (precios, horarios, accesibilidad)

### Experiencia de Usuario

- Recomendaciones personalizadas por perfil familiar
- Búsqueda conversacional intuitiva
- Respuestas formateadas en Markdown
- Filtros accesibles (carrito, cambiador, interior, mascotas, etc.)

### Performance

- Caché local para optimización
- Procesamiento en tiempo real (~2-3 segundos)
- Escalable para múltiples usuarios
- APIs REST bien definidas

---

## Estructura del Proyecto

```
Desafio-Data/
│
├── README.md                    # Este archivo
├── docker-compose.yml           # Orquestación de contenedores
├── Dockerfile                   # Imagen Docker del proyecto
│
├── models/                      # Sistemas de IA
│   ├── Recommender/             # Sistema de recomendación
│   │   ├── app.py              # API Flask del recomendador
│   │   ├── recommender.py       # Lógica de scoring y perfil
│   │   ├── config.py           # Configuración centralizada
│   │   ├── data_access.py      # Acceso a BD y embeddings
│   │   ├── location.py         # Detección de municipios
│   │   └── requirements.txt
│   │
│   └── Chatbot/                 # Asistente conversacional
│       ├── app5.py             # API Flask del chatbot
│       ├── API_LLM.py          # Motor de procesamiento
│       ├── requirements.txt
│       ├── report.md           # Informe técnico
│       └── old_versions/       # Versiones anteriores
│
├── data/                        # Datos del proyecto
│   ├── descargas/              # Datasets CSV
│   │   ├── events_*.csv        # Eventos del sistema
│   │   ├── families.csv        # Perfiles familiares
│   │   ├── users.csv           # Usuarios
│   │   └── ...
│   ├── embeddings/             # Embeddings precalculados
│   │   ├── embeddings.npy      # Matriz de vectores
│   │   └── embeddings_index.csv # Mapeo id → índice
│   └── eventos.db              # Base de datos SQLite
│
├── documentation/               # Documentación del proyecto
│   ├── chatbot.md               # Memoria técnica del chatbot
│   ├── datos.md                 # Memoria técnica de datos
│   └── recommender.md           # Memoria técnica del recomendador
│
├── notebooks/                   # Notebooks de análisis
│   ├── embedder_multilingual_e5.ipynb
│   ├── comparativa_embeddings.ipynb
│   ├── multilingual_large_embedding.ipynb
│   └── sql_eventos.ipynb
│
└── database/                    # Configuración de base de datos
```

---

## Componentes del Sistema

### 1. Sistema de Recomendación (`models/Recommender/`)

**Propósito**: Recomendaciones personalizadas basadas en similitud semántica y perfil del usuario.

**Flujo**:

```
Usuario busca: "Museo en Bilbao para pasar un día en familia"
                    ↓
            Análisis de consulta
            Lectura de perfil (edades, mascotas)
            Revisión de historial (eventos visitados)
                    ↓
            Construcción de vector de perfil
            (media ponderada de experiencias positivas)
                    ↓
            Cálculo de similitud semántica:
            Score = α·sim(consulta) + β·sim(perfil) - penalización
                    ↓
            Aplicación de filtros duros
            (accesibilidad, precio, etc.)
                    ↓
            Ranking de eventos por score
            Aplicación de boost para promocionados
                    ↓
            Respuesta: Top 10 eventos personalizados
```

**Tecnologías**:

- Embeddings: `intfloat/multilingual-e5-large`
- Similitud: Coseno (producto escalar sobre vectores normalizados)
- BD: SQLite con historial, favoritos, perfiles familiares
- Framework: Flask REST API

### 2. Chatbot Conversacional (`models/Chatbot/`)

**Propósito**: Búsqueda intuitiva en lenguaje natural con enriquecimiento automático.

**Flujo**:

```
Usuario pregunta: "Eventos gratis para niños esta semana sin lluvia"
                    ↓
            API REST recibe consulta
                    ↓
            LLM (Ollama) analiza la consulta en lenguaje natural
            Genera código Python de filtrado automático
                    ↓
            Descarga eventos desde API Euskadi
            Enriquecimiento con datos meteorológicos (Open-Meteo)
            Construcción de DataFrame Pandas
                    ↓
            Aplicación del filtro generado:
            df[(df['price']==0) & (df['is_infantil']==True) & 
               (df['precipitation']<30) & (df['week']==current_week)]
                    ↓
            Formateo de respuesta en Markdown
                    ↓
            Respuesta: Eventos filtrados con clima, precios, imágenes
```

**Tecnologías**:

- LLM: Ollama (local, sin cloud)
- APIs: Euskadi, Open-Meteo
- Procesamiento: Pandas DataFrame
- Framework: Flask REST API

---

## Instalación Rápida

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/urkomen/Desafio-Data.git
cd Desafio-Data

# 2. Compilar y ejecutar con Docker Compose
docker-compose up -d

# Los servicios estarán disponibles en:
# - Recomendador: http://localhost:5000
# - Chatbot: http://localhost:5001
```

### Opción 2: Instalación Local

#### Recomendador

```bash
cd models/Recommender
pip install -r requirements.txt
python app.py
# Disponible en: http://localhost:5000
```

#### Chatbot (requiere Ollama)

```bash
# Primero, instalar y ejecutar Ollama
curl https://ollama.ai/install.sh | sh
ollama serve

# En otra terminal:
cd models/Chatbot
pip install -r requirements.txt
python app5.py
# Disponible en: http://localhost:5001
```

---

## Guía de Uso

### Acceso a los Servicios

| Servicio                 | URL                       | Descripción                          |
| ------------------------ | ------------------------- | ------------------------------------- |
| **Recomendador**   | `http://localhost:5000` | API de recomendaciones personalizadas |
| **Chatbot**        | `http://localhost:5001` | API conversacional                    |
| **Documentación** | `/documentation/`       | Memorias y guías técnicas           |

### Autenticación

Actualmente sin autenticación requerida (desarrollo). Para producción, añadir tokens JWT.

### Rate Limiting

No implementado aún. Considerar para versiones futuras.

---

## Ejemplos Prácticos

### Ejemplo 1: Usar el Recomendador

**Scenario**: Usuario con familia de 2 adultos, 2 niños (7 y 10 años), con mascota.

**Request**:

```bash
curl -X POST http://localhost:5000/recomendar \
  -H "Content-Type: application/json" \
  -d '{
    "id_user": 42,
    "consulta": "Actividades al aire libre para pasar un fin de semana en familia",
    "filtros": {
      "carrito": false,
      "cambiador": false,
      "interior": false,
      "accesible": false,
      "mascota": true,
      "gratis": false
    }
  }'
```

**Response**:

```json
{
  "recomendaciones": [
    {
      "evento_id": 8945,
      "nombre": "Parque Natural de Gorbeia - Senderismo Familiar",
      "municipio": "Ausa",
      "categoria": "Naturaleza",
      "price": 5.50,
      "score": 0.9234,
      "ranking": 1,
      "razon": "Alta similitud con actividades al aire libre + mascotas permitidas",
      "website": "https://..."
    },
    {
      "evento_id": 7634,
      "nombre": "Aventura en Tirolesa - Bosque de Otzarreta",
      "municipio": "Orozko",
      "categoria": "Aventura",
      "price": 12.0,
      "score": 0.8876,
      "ranking": 2,
      "razon": "Perfecta para familias con niños, ambiente natural"
    }
    // ... más recomendaciones
  ],
  "total": 127,
  "filtrados": 45,
  "tiempo_procesamiento_ms": 245
}
```

**Interpretación**:

- Se encontraron 127 eventos relacionados
- Se filtraron a 45 por los criterios dados
- Se recomiendan los 2 mejores basados en similitud con consulta + perfil familiar
- Tiempo de respuesta: 245ms

---

### Ejemplo 2: Usar el Chatbot

**Scenario**: Usuario busca eventos para este domingo sin lluvia.

**Request**:

```bash
curl "http://localhost:5001/Que%20hacer%20este%20domingo%20sin%20lluvia%20en%20Bilbao"
```

**Response** (Markdown):

```markdown
# Resultados para: "Que hacer este domingo sin lluvia en Bilbao"

## Museo Guggenheim Bilbao
**Ubicación:** Bilbao, Abando  
**Fecha:** 8 de junio de 2026 (Domingo)  
**Hora:** 10:00 - 19:00  
**Precio:** 13€ (Adultos), 7€ (Menores)  
**Idioma:** Español/Euskera/Inglés

### Clima Esperado
- **Temperatura:** 22°C
- **Humedad:** 45%
- **Viento:** 5 km/h
- **Probabilidad lluvia:** 5%
- **Recomendación:** Condiciones excelentes

### Descripción
Exposición temporal: "Surrealismo: Viajes por lo Desconocido" con obras de Dalí, Magritte y De Chirico. Visita guiada a las 12:00.

### Galería
![Guggenheim](https://...)

---

## Centro Cultural Azkena - Concierto de Jazz
**Ubicación:** Bilbao, Casco Viejo  
**Fecha:** 8 de junio de 2026 (Domingo)  
**Hora:** 20:00  
**Precio:** Gratis (Entrada hasta completar aforo)  
**Idioma:** Español

### Clima Esperado
- **Probabilidad lluvia:** 10%
- **Temperatura:** 20°C (para la tarde)

### Descripción
Actuación de "The Blue Cats" - Trío de jazz tradicional en directo...

---
```

**Interpretación**:

- El chatbot entendió la consulta en lenguaje natural
- Filtró automáticamente por ubicación (Bilbao) y condiciones climáticas
- Enriqueció con datos meteorológicos en tiempo real
- Presentó resultados listos para mostrar (Markdown)

---

### Ejemplo 3: Flujo Completo de Usuario

**Día 1: Nuevo Usuario**

1. Usuario se registra en la plataforma
2. Completa perfil familiar (edades, mascotas, preferencias)
3. Usa el **Chatbot** para buscar: "Planes para familias con niños pequeños"
4. Recibe recomendaciones inmediatas sin historial previo

**Día 7: Usuario con Historial**

1. Usuario ha visitado 3 eventos (2 con rating 5 estrellas, 1 con rating 4 estrellas)
2. Usa el **Recomendador** (mejor con historial): "Busco algo parecido a lo que me encantó"
3. Sistema detecta patrón: "Le encantaron museos y exposiciones"
4. Recibe recomendaciones más personalizadas
5. Ajusta ponderación: 50% consulta + 50% perfil (vs 90% + 10% para nuevos)

---

## Arquitectura Técnica

### Stack Tecnológico

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
    │   Recomendador    │    │   Chatbot (Ollama)    │
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

### Flujo de Datos

```
Usuario Request
    ↓
    ├─→ [Recomendador]
    │   • Lee perfil usuario (BD)
    │   • Crea embedding perfil usuario
    │   • Lee historial (BD)
    │   • Busca embeddings (NPY)
    │   • Calcula scores
    │   • Aplica filtros
    │   ↓
    │   Response: Top 10 eventos personalizados
    │
    └─→ [Chatbot]
        • LLM interpreta lenguaje natural
        • Genera filtro Python
        • Descarga eventos (API Euskadi)
        • Enriquece con clima (Open-Meteo)
        • Formatea respuesta
        ↓
        Response: Eventos filtrados + clima
```

---

## Requisitos

### Software

- Python 3.8+
- Docker & Docker Compose (recomendado)
- Ollama (para Chatbot)

### Hardware (Mínimo)

- RAM: 4 GB
- Disco: 5 GB
- CPU: Dual Core

### Hardware (Recomendado para Producción)

- RAM: 16 GB
- Disco: 20 GB
- CPU: Quad Core
- GPU: Opcional (mejora performance de LLM)

### Conexión

- Internet para APIs (Euskadi, Open-Meteo)
- HTTPS recomendado para producción

---

## Documentación Completa

### Documentos Técnicos

| Documento                      | Ubicación                       | Descripción                                                     |
| ------------------------------ | -------------------------------- | ---------------------------------------------------------------- |
| **README Recomendador**  | `documentation/recommender.md` | Guía técnica del motor de recomendación                       |
| **README Chatbot**       | `documentation/chatbot.md `    | Guía técnica del asistente conversacional                      |
| **README Datos**         | `documentation/datos.md`       | Guía e información sobre los datos                             |
| **Memoria Recomendador** | `memoria.md`                   | Descripción, decisiones, estructura y conclusiones del proyecto |

### Notebooks de Análisis

| Notebook                           | Propósito                       |
| ---------------------------------- | -------------------------------- |
| `embedder_multilingual_e5.ipynb` | Generación de embeddings        |
| `comparativa_embeddings.ipynb`   | Análisis comparativo de modelos |
| `sql_eventos.ipynb`              | Exploración de base de datos    |

---

## Roadmap

### Fase 1: MVP (Día 1)

- [ ] Chatbot recibe input y devuelve eventos
- [ ] Recomendador devuelve lista de eventos
- [ ] Datos ficticios en ficheros

### Fase 2: Mejoras de consultas (Días 2-4)

- [ ] El chatbot devuelve información visualmente y consulta el clima
- [ ] Se vectorizan planes y usuarios
- [ ] Datos reales

### Fase 3: Consultas muy personalizadas (Días 4-5)

- [ ] Se optimiza el chatbot para responder mucho más rápido y la IA consulta bases de datos
- [ ] Score_final  + boost promocional
- [ ] Creamos tablas de datos y se usan de consulta

### Fase 4: Conexión entre modelos (Futuro)

- [ ] Conectar chatbot al motor recomendador, mejoras estéticas y funcionales extra
- [ ] Tener en cuenta similitud entre diferentes usuarios
- [ ] Mejorar la calidad de datos con limpieza más exhaustiva

---

## Soporte y Contacto

### Reportar Bugs

Crear issue en: https://github.com/urkomen/Desafio-Data/issues

### Sugerencias

Discusiones: https://github.com/urkomen/Desafio-Data/discussions

### Licencia

Especificar aquí (MIT, GPL, etc.)

---

## Contribuidores

- Urko Menendez
- Ruben Novoa
- Danillo Barros de Souza
- Oscar Fernandez

---

## Referencias y Recursos

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

---

## Estadísticas del Proyecto

| Métrica                  | Valor                              |
| ------------------------- | ---------------------------------- |
| Eventos Indexados         | ~500                               |
| Embeddings Precalculados  | 1024 dimensiones                   |
| Usuarios Soportados       | Escalable                          |
| Tiempo Respuesta Promedio | 2-3s (caché) / 8-12s (sin caché) |
| Idiomas Soportados        | 3 (ES, EU, FR)                     |
| APIs Integradas           | 3 (Euskadi, Open-Meteo, Ollama)    |

---

**Última actualización**: Junio 2026
**Versión**: 2.0
**Estado**: 🟢 Producción

---

## 🎯 Quick Start Checklist

- [ ] Clonar repositorio
- [ ] Instalar Docker o dependencias locales
- [ ] Ejecutar servicios (Docker Compose o manual)
- [ ] Probar Recomendador: `curl http://localhost:5000`
- [ ] Probar Chatbot: `curl http://localhost:5001`
- [ ] Leer documentación en `documentation/`
- [ ] Explorar notebooks en `notebooks/`
- [ ] ¡Empezar a usar!

---

**¿Preguntas?** Consulta la documentación en `/documentation/` o revisa los READMEs específicos de cada componente.
