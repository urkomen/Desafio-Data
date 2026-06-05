from datetime import datetime
import re
from html import unescape
import pandas as pd
import requests
import ollama
import sys

VENT_TYPES_API = "https://api.euskadi.eus/culture/events/v1.0/eventType"
UPCOMING_EVENTS_API = "https://api.euskadi.eus/culture/events/v1.0/events/upcoming"

question = sys.argv[1]

def get_event_types():
    r = requests.get(EVENT_TYPES_API)
    return r.json()


def get_upcoming_events():
    r = requests.get(UPCOMING_EVENTS_API)
    return r.json()

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

def format_events_md(events: list[dict], lang: str = "Es") -> str:
    return "\n\n".join(format_event_md(e, lang) for e in events)
lang_dict={"ES":"Español","EU":"Euskera","FR":"Francés"}
upcoming_events=get_upcoming_events()
I=pd.DataFrame(upcoming_events["items"])
I["language"]=[lang_dict[i] if i in lang_dict.keys() else i for i in I.language]
I["language"]=I.language.fillna("No informado")

I["priceEs"]=I["priceEs"].fillna("No informado")
I["urlNameEs"]=I.urlNameEs.fillna("Información en la imagen")
I["purchaseUrlEs"]=I.purchaseUrlEs.fillna("No informado")
I["startDate"] = pd.to_datetime(I["startDate"])
I["endDate"] = pd.to_datetime(I["endDate"])

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

I.language.unique()
{I.language.unique()}

I.municipalityEs.unique():
{I.municipalityEs}

I.startDate.unique():
{I.startDate.unique()}

I.endDate.unique():
{I.endDate.unique()}

I.priceEs.unique():
{I.priceEs.unique()}

I.typeEs.unique():
{I.typeEs.unique()}

I.language.unique():
{I.language.unique()}

return ONLY the corresponding Python code that will return the asked question.
Example: "What types of events exist?"
Answer: "I.typeEs.unique()"

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
assignment=make_assignment(model_query)
Filter=apply_filter(assignment)
#print(Filter)
try:
    results=list(Filter.T.to_dict().values())
except:
    results=[]
try:
    print(format_events_md(results))

except Exception as e:
    error_msg = (
        "---\n"
        "Lo sentimos mucho. No hemos encontrado las informaciones con los filtros de tu búsqueda.\n"
        "---"
    )
    print(error_msg)