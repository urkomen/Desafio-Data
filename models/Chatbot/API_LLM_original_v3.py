from datetime import datetime
import re
from html import unescape
import pandas as pd
import requests
import ollama
import sys
import requests
from datetime import datetime, timedelta
import os

VENT_TYPES_API = "https://api.euskadi.eus/culture/events/v1.0/eventType"
#UPCOMING_EVENTS_API = "https://api.euskadi.eus/culture/events/v1.0/events/upcoming"
UPCOMING_EVENTS_API = "https://api.euskadi.eus/culture/events/v1.0/events/upcoming?_elements=5000"

question = sys.argv[1]

def get_event_types():
    r = requests.get(EVENT_TYPES_API)
    return r.json()


def get_upcoming_events():
    # Blindaje del consumo externo: ante fallo de red, JSON inválido o ausencia
    # de "items", devolvemos una estructura segura en vez de propagar el traceback.
    try:
        r = requests.get(UPCOMING_EVENTS_API, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return {"items": []}
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return {"items": []}
    return data

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    return re.sub(r"<[^>]+>", "", text).strip()


def fmt_date(d: str) -> str:
    try:
        return datetime.fromisoformat(d.replace("Z", "")).strftime("%Y-%m-%d")
    except Exception:
        return d


def extract_image(event: dict) -> str:
    """
    Returns markdown image string if available, otherwise empty string.
    """
    images = event.get("images", [])
    if images and isinstance(images, list):
        img = images[0]
        url = img.get("imageUrl")
        alt = img.get("imageFileName", "event image")
        if url:
            return f"![{alt}]({url})\n"
    return ""


MONTHS_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

def fmt_date(date_str):
    if not date_str:
        return ""

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        return dt.date().strftime("%Y-%m-%d")  # ONLY date, no time at all
    except Exception:
        return date_str

def is_valid(value):
    return value is not None and str(value).strip().lower() not in ["", "nan", "none"]

def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "Sin nombre")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "Sin fecha"

    municipality = event.get(f"municipality{lang}", "Sin municipio")

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "Sin lugar"
    )

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "Sin precio")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "Sin web"
    )

    language = event.get("language", "Sin idioma")

    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}
**📅 Fecha:** {date}  
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {website}

### 📝 Descripción
{description}

---
"""

def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "Sin nombre")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "Sin fecha"

    municipality = event.get(f"municipality{lang}", None)

    place = event.get(f"establishment{lang}") or municipality

    if not is_valid(place):
        place = None

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "Sin precio")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "Sin web"
    )

    language = event.get("language", "Sin idioma")

    image_md = extract_image(event)

    # ---- build markdown dynamically ----
    lines = [
        f"## 🎭 {name}",
        "---",
        image_md,
        f"**📅 Fecha:** {date}",
    ]

    if is_valid(municipality):
        lines.append(f"**🏙️ Municipio:** {municipality}")

    if is_valid(place):
        lines.append(f"**📍 Lugar:** {place}")

    lines += [
        f"**🗣️ Idioma:** {language}",
        f"**💶 Precio:** {price}",
        f"**🌐 Web:** {website}",
        "",
        "### 📝 Descripción",
        description,
        "---",
    ]

    return "\n".join(lines)


MONTHS_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

def fmt_date(date_str):
    if not date_str:
        return ""

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))

        # If time is midnight, show only the date
        if dt.hour == 0 and dt.minute == 0:
            return f"{dt.day} de {MONTHS_ES[dt.month]} de {dt.year}"

        # Otherwise show date only (NO time info)
        return dt.strftime("%Y-%m-%d")

    except Exception:
        return date_str


def is_valid(value):
    return value is not None and str(value).strip().lower() not in ["nan", "none", ""]


def extract_image(event: dict) -> str:
    """
    Returns markdown image string if available, otherwise empty string.
    """
    images = event.get("images", [])
    if images and isinstance(images, list):
        img = images[0]
        url = img.get("imageUrl")
        alt = img.get("imageFileName", "event image")
        if url:
            return f"![{alt}]({url})\n"
    return ""


def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "No informado")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "No informado"

    municipality = event.get(f"municipality{lang}", "Sin municipio")
    if not is_valid(municipality):
        municipality = ""

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "No informado"
    )

    if not is_valid(place):
        place = "Consultar Web"

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "No informado")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "No informado"
    )

    language = event.get("language", "No informado")

    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}
**📅 Fecha:** {date}  
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {website}

### 📝 Descripción
{description}

---
"""

def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "No informado")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "No informado"

    municipality = event.get(f"municipality{lang}", "Sin municipio")
    if not is_valid(municipality):
        municipality = ""

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "No informado"
    )

    if not is_valid(place):
        place = "Consultar Web"

    event_type = event.get(f"type{lang}", event.get("type", "No informado"))

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "No informado")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "No informado"
    )

    language = event.get("language", "No informado")

    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}
**📅 Fecha:** {date}  
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🎟️ Tipo de evento:** {event_type}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {website}

### 📝 Descripción
{description}

---
"""

def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "No informado")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "No informado"

    municipality = event.get(f"municipality{lang}", "Sin municipio")
    if not is_valid(municipality):
        municipality = ""

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "No informado"
    )

    if not is_valid(place):
        place = "Consultar Web"

    event_type = event.get(f"type{lang}", event.get("type", "No informado"))

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "No informado")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "No informado"
    )

    language = event.get("language", "No informado")

    # --- NEW: coordinates ---
    lat = event.get("municipalityLatitude")
    lon = event.get("municipalityLongitude")

    if is_valid(lat) and is_valid(lon):
        map_link = f"[Pincha para ver el Mapa](https://www.google.com/maps?q={lat},{lon})"
    else:
        map_link = "Mapa no disponible"

    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}
**📅 Fecha:** {date}  
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🎟️ Tipo de evento:** {event_type}  
**🗺️ Mapa:** {map_link}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {website}

### 📝 Descripción
{description}

---
"""

def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "No informado")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "No informado"

    municipality = event.get(f"municipality{lang}", "Sin municipio")
    if not is_valid(municipality):
        municipality = ""

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "No informado"
    )

    if not is_valid(place):
        place = "Consultar Web"

    event_type = event.get(f"type{lang}", event.get("type", "No informado"))

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "No informado")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "No informado"
    )

    language = event.get("language", "No informado")

    # NEW: opening hours
    opening_hours = event.get(f"openingHours{lang}", "")
    opening_hours = clean_html(opening_hours) if opening_hours else "No informado"

    # Coordinates
    lat = event.get("municipalityLatitude")
    lon = event.get("municipalityLongitude")

    if is_valid(lat) and is_valid(lon):
        map_link = f"[Pincha para ver el Mapa](https://www.google.com/maps?q={lat},{lon})"
    else:
        map_link = "Mapa no disponible"

    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}
**📅 Fecha:** {date}  
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🎟️ Tipo de evento:** {event_type}  
**🗺️ Mapa:** {map_link}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {website}

### 📝 Descripción
{description}

### 🕒 Horarios
{opening_hours}

---
"""

def format_events_md(events: list[dict], lang: str = "Es") -> str:
    return "\n\n".join(format_event_md(e, lang) for e in events)

lang_dict={"ES":"Español","EU":"Euskera","FR":"Francés"}

CSV_PATH = "events_weather.csv"
CACHE_HOURS = 6


# =========================
# WEATHER FUNCTION
# =========================
def get_weather_info(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability"
        "&forecast_days=1"
    )

    data = requests.get(url).json()

    times = data["hourly"]["time"]

    # current time rounded + offset logic (your original logic preserved)
    next_hour = (
        (datetime.utcnow() + timedelta(hours=2))
        .replace(minute=0, second=0, microsecond=0)
        + timedelta(hours=6)
    )

    target_time = next_hour.strftime("%Y-%m-%dT%H:00")

    if target_time in times:
        idx = times.index(target_time)

        return {
            "last_updated": datetime.utcnow() + timedelta(hours=2),
            "time": target_time,
            "temperature": data["hourly"]["temperature_2m"][idx],
            "humidity": data["hourly"]["relative_humidity_2m"][idx],
            "wind_speed": data["hourly"]["wind_speed_10m"][idx],
            "precipitation_probability":data["hourly"]["precipitation_probability"][idx],
        }

    return {
        "last_updated": datetime.utcnow() + timedelta(hours=2),
        "time": "No informado",
        "temperature": "No informado",
        "humidity": "No informado",
        "wind_speed": "No informado",
        "precipitation_probability":"No informado",
    }

def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "No informado")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "No informado"

    municipality = event.get(f"municipality{lang}", "Sin municipio")
    if not is_valid(municipality):
        municipality = ""

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "No informado"
    )

    if not is_valid(place):
        place = "Consultar Web"

    event_type = event.get(f"type{lang}", event.get("type", "No informado"))

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "No informado")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "No informado"
    )

    language = event.get("language", "No informado")

    # --- Opening hours ---
    opening_hours = event.get(f"openingHours{lang}", "")
    opening_hours = clean_html(opening_hours) if is_valid(opening_hours) else "No informado"

    # --- Weather info ---
    temperature = event.get("temperature")
    humidity = event.get("humidity")
    wind_speed = event.get("wind_speed")
    precipitation = event.get("precipitation_probability")

    def fmt(val, suffix=""):
        return f"{val}{suffix}" if is_valid(val) else "No informado"

    weather_md = f"""
### 🌤️ Condiciones meteorológicas (próximas 6 horas)*
- 🌡️ Temperatura: {fmt(temperature, "°C")}
- 💧 Humedad: {fmt(humidity, "%")}
- 🌬️ Viento: {fmt(wind_speed, " km/h")}
- 🌧️ Precipitación: {fmt(precipitation, "%")}

*Ultima atualización: {I.last_updated[0]}
"""

    # --- Coordinates ---
    lat = event.get("municipalityLatitude")
    lon = event.get("municipalityLongitude")

    if is_valid(lat) and is_valid(lon):
        map_link = f"[Pincha para ver el Mapa](https://www.google.com/maps?q={lat},{lon})"
    else:
        map_link = "Mapa no disponible"

    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}
**📅 Fecha:** {date}  
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🎟️ Tipo de evento:** {event_type}  
**🗺️ Mapa:** {map_link}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {website}  
**🕒 Horario:** {opening_hours}

{weather_md}

### 📝 Descripción
{description}

---
"""

import ast

def extract_image(event: dict) -> str:
    raw_images = event.get("images")

    if not raw_images:
        return ""

    try:
        # Handle stringified list from dataframe
        if isinstance(raw_images, str):
            images = ast.literal_eval(raw_images)
        else:
            images = raw_images

        if isinstance(images, list) and len(images) > 0:
            first = images[0]
            url = first.get("imageUrl")

            if url:
                return f"![Event image]({url})"

    except Exception:
        pass

    return ""


def format_event_md(event: dict, lang: str = "Es") -> str:
    name = event.get(f"name{lang}", "No informado")

    start_date = event.get("startDate", "")
    end_date = event.get("endDate", "")

    if start_date and end_date:
        #date = f"{fmt_date(start_date)} → {fmt_date(end_date)}"
        date = f"{str(fmt_date(start_date))[:-15]}"
    elif start_date:
        date = fmt_date(start_date)
    elif end_date:
        date = fmt_date(end_date)
    else:
        date = "No informado"

    municipality = event.get(f"municipality{lang}", "Sin municipio")
    if not is_valid(municipality):
        municipality = ""

    place = (
        event.get(f"establishment{lang}")
        or municipality
        or "No informado"
    )

    if not is_valid(place):
        place = "Consultar Web"

    event_type = event.get(f"type{lang}", event.get("type", "No informado"))

    description = clean_html(event.get(f"description{lang}", ""))

    price = event.get(f"price{lang}", "No informado")

    website = (
        event.get(f"sourceUrl{lang}")
        or event.get(f"urlEvent{lang}")
        or "No informado"
    )

    language = event.get("language", "No informado")

    # --- Opening hours ---
    opening_hours = event.get(f"openingHours{lang}", "")
    opening_hours = clean_html(opening_hours) if is_valid(opening_hours) else "No informado"

    # --- Weather ---
    temperature = event.get("temperature")
    humidity = event.get("humidity")
    wind_speed = event.get("wind_speed")
    precipitation = event.get("precipitation_probability")

    def fmt(val, suffix=""):
        return f"{val}{suffix}" if is_valid(val) else "No informado"

    weather_md = f"""
### 🌤️ Condiciones meteorológicas (Próximas 6 horas)*
- 🌡️ Temperatura: {fmt(temperature, "°C")}
- 💧 Humedad: {fmt(humidity, "%")}
- 🌬️ Viento: {fmt(wind_speed, " km/h")}
- 🌧️ Precipitación: {fmt(precipitation, "%")}

*Última atualización: {I.last_updated[0][:-7]}
"""

    # --- Coordinates ---
    lat = event.get("municipalityLatitude")
    lon = event.get("municipalityLongitude")

    if is_valid(lat) and is_valid(lon):
        map_link = f"[Pincha para ver en Maps](https://www.google.com/maps?q={lat},{lon})"
    else:
        map_link = "Mapa no disponible"

    # --- Image ---
    image_md = extract_image(event)

    return f"""## 🎭 {name}

---

{image_md}

**📅 Fecha:** {date}
**🕒 Horario:** {opening_hours}
**🏙️ Municipio:** {municipality}  
**📍 Lugar:** {place}  
**🎟️ Tipo de evento:** {event_type}  
**🗺️ Mapa:** {map_link}  
**🗣️ Idioma:** {language}  
**💶 Precio:** {price}  
**🌐 Web:** {f"[Pincha para ver el enlace]({website})"}

{weather_md}

### 📝 Descripción
{description}

---
"""
# =========================
# CACHE VALIDATION
# =========================
def is_cache_valid(path, hours=6):
    if not os.path.exists(path):
        return False

    file_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.utcnow() - file_time < timedelta(hours=hours)


# =========================
# MAIN LOGIC
# =========================
def build_dataframe():
    upcoming_events = get_upcoming_events()
    I = pd.DataFrame(upcoming_events["items"])

    # Garantiza columnas esperadas aunque la API las omita en algún evento.
    for col in ("municipalityEs", "municipalityLatitude", "municipalityLongitude"):
        if col not in I.columns:
            I[col] = None

    # ---- Build municipality -> (lat, lon)
    # Se saltan municipios nulos/vacíos y los que no tienen coordenadas resolubles;
    # nunca se accede a [0] sobre una lista vacía.
    M = {}
    for m in I.municipalityEs.unique():
        if not is_valid(m):
            continue
        lats = I[I.municipalityEs == m].municipalityLatitude.dropna().unique()
        lons = I[I.municipalityEs == m].municipalityLongitude.dropna().unique()
        if len(lats) == 0 or len(lons) == 0:
            continue
        M[m] = (lats[0], lons[0])

    # ---- Get weather per municipality (si el lookup falla, se omite ese municipio)
    W = {}
    for m in M.keys():
        try:
            W[m] = get_weather_info(*M[m])
        except Exception:
            continue

    # ---- Valores seguros para eventos sin municipio/clima resoluble
    DEFAULT_WEATHER = {
        "temperature": "No informado",
        "humidity": "No informado",
        "wind_speed": "No informado",
        "time": "No informado",
        "last_updated": "No informado",
        "precipitation_probability": "No informado",
    }

    def weather_value(municipality, key):
        info = W.get(municipality)
        return info.get(key, DEFAULT_WEATHER[key]) if info else DEFAULT_WEATHER[key]

    # ---- Merge into dataframe (sin acceso por clave directa: evita KeyError con municipio nulo)
    for key in (
        "temperature",
        "humidity",
        "wind_speed",
        "time",
        "last_updated",
        "precipitation_probability",
    ):
        I[key] = [weather_value(m, key) for m in I.municipalityEs]

    return I


# =========================
# LOAD OR REFRESH
# =========================
if is_cache_valid(CSV_PATH, CACHE_HOURS):
    #print("📂 Loading cached data...")
    I = pd.read_csv(CSV_PATH)

else:
    #print("🔄 Recomputing data...")
    I = build_dataframe()

    #print("💾 Saving cache...")
    I.to_csv(CSV_PATH, index=False)


# ──────────────────────────────────────────────────────────────
# PUERTA DEFENSIVA DE COLUMNAS
# Garantiza, en un único sitio, las columnas que el resto del módulo asume
# (accesos directos y el SYSTEM_PROMPT con .unique()). Si la API de Euskadi
# omite alguna o la caché es parcial, se crea con valor seguro y así un único
# evento/payload incompleto no tumba el arranque del script.
# ──────────────────────────────────────────────────────────────
COLUMNAS_ESPERADAS = [
    "nameEs", "municipalityEs", "openingHoursEs", "language",
    "startDate", "endDate", "priceEs", "typeEs", "urlNameEs", "purchaseUrlEs",
    "temperature", "humidity", "wind_speed", "precipitation_probability",
]
for _col in COLUMNAS_ESPERADAS:
    if _col not in I.columns:
        I[_col] = "No informado"


#upcoming_events=get_upcoming_events()
#I=pd.DataFrame(upcoming_events["items"])

I["language"]=[lang_dict[i] if i in lang_dict.keys() else i for i in I.language]
I["language"]=I.language.fillna("No informado")

I["priceEs"]=I["priceEs"].fillna("No informado")
I["urlNameEs"]=I.urlNameEs.fillna("Información en la imagen")
I["purchaseUrlEs"]=I.purchaseUrlEs.fillna("No informado")
# errors="coerce": fechas fuera de rango/inválidas pasan a NaT en vez de lanzar
# OverflowError (algún evento de Euskadi trae fechas que desbordan pandas).
I["startDate"] = pd.to_datetime(I["startDate"], errors="coerce")
I["endDate"] = pd.to_datetime(I["endDate"], errors="coerce")

SYSTEM_PROMPT = f"""
You are a strict code-only assistant that will provide code answers based on a naive python user.
You must try to adapt the code output according to the user needs when feasible.

RULES:
- You MUST ignore all personal, emotional, or unrelated questions.
- Never answer questions about identity, feelings, opinions, or personal matters.
- Only respond with valid Python code using the provided CONTEXT.
- If the question is not answerable using the context, return: ```python pd.DataFrame()```.
- Do not explain anything.
- Do not add comments.
- Output ONLY Python code.


avoid filters like .head() and I[column], I.column, startDate.unique() if not asked

CONTEXT

Títulos / nombres de los eventos:
I.nameEs.unique():
{I.nameEs.unique()}

Probabilidad de lluvia:
I.precipitation_probability.unique():
{I.precipitation_probability.unique()}

Temperatura:
I.temperature.unique()
{I.temperature.unique()}

Tempetura alta caliente: superior a 17 grados
Temperatura buena agradable: inferior a 17 grados

Humedad:
I.humidity.unique()
{I.humidity.unique()}

Velocidad del Vento:
I.wind_speed.unique()
{I.wind_speed.unique()}

Horarios:
I.openingHoursEs.unique()
{I.openingHoursEs.unique()}

Horarios de final de tarde: Despues de las 16.
Horarios de inicio de tarde: Antes de las 16.

Idiomas:
I.language.unique()
{I.language.unique()}

Municipios/ciudades/localidades:
I.municipalityEs.unique():
{I.municipalityEs}

Fecha de início:
I.startDate.unique():
{I.startDate.unique()}

Fecha de término:
I.endDate.unique():
{I.endDate.unique()}

Precios:
I.priceEs.unique():
{I.priceEs.unique()}

Precios caros: Superior a 50 
Precios baratos: Inferior a 50 o gratis

Tipos de eventos:
I.typeEs.unique():
{I.typeEs.unique()}

Idiomas:
I.language.unique():
{I.language.unique()}

return ONLY the corresponding Python code that will return the asked question.
Example: "Eventos que ocurren en Mayo"
Answer: "I[I.openingHoursEs.str.contains("mayo")]"

REMARK: If the user asks "sorpendeme" return a random filter over the variable I and return it.
REMARK: Search similar information from the event title when asked.

"""

def ask_model(question):

    user_prompt = f"""

QUESTION:
{question}
"""

    reply = ollama.chat(
        model="qwen2.5-coder:latest",
        #model="qwen2.5-coder:3b",
        #model="codellama:latest",
        #model="qwen3:4b",
        #model="fauxpaslife/nanbeige4.1-python-deepthink:3b",

        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        options={"temperature": 0.1,
        "top_p":0.2}
    )

    return reply["message"]["content"]

import re

def make_assignment(llm_output):
    match = re.search(r"```(?:python)?\n(.*?)\n```", llm_output, re.DOTALL)
    if not match:
        raise ValueError("No Python code block found")

    expression = match.group(1).strip()
    return f"{expression}"

def apply_filter(expr):
    global I0
    try:
        I0 = eval(expr)
    except:
        I0=None
    return I0

#question="I want to know about free events in bilbao"
#print(question)
model_query=ask_model(question)
#print(model_query)
try:
    assignment=make_assignment(model_query)
except ValueError:
    # El LLM no devolvió un bloque ```python``` válido: caemos a un filtro vacío
    # para que el flujo muestre el mensaje amable en vez de un traceback/ERROR.
    assignment="pd.DataFrame()"
Filter=apply_filter(assignment)
#print(Filter)
try:
    results=list(Filter.T.to_dict().values())
    
except:
    #results=[]
    results=list(I.T.to_dict().values())
try:
    if len(results)!=0:
        print(format_events_md(results))
    else:
        results=list(I.T.to_dict().values())
        print(print(f"""---
⚠️ No hemos encontrado información que coincida con los filtros de tu búsqueda.

Te recomendamos reformular la consulta o intentar describirla de otra manera.

De todas formas, a continuación te mostramos los eventos disponibles para hoy.

{format_events_md(results)}
---"""))

except Exception as e:
    error_msg = (
        """---
⚠️ No hemos encontrado información que coincida con los filtros de tu búsqueda.

Te recomendamos reformular la consulta o intentar describirla de otra manera.

De todas formas, a continuación te mostramos los eventos disponibles para hoy.
---"""
    )
    print(error_msg)
