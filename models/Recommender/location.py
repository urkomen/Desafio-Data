"""
Detección del municipio dentro del texto libre de búsqueda.

La columna 'municipio' de eventos tiene 458 valores, muchos compuestos
(separados por ';') y bilingües (separados por '/', p.ej.
"Donostia / San Sebastián", "Arrasate / Mondragón").

Se construye un catálogo de alias -> término canónico de búsqueda.
Al recibir el texto del usuario se busca qué alias aparece (por palabra
completa, sin distinguir mayúsculas/acentos), priorizando el alias más
largo para evitar falsos positivos por subcadenas.
"""
import re
import unicodedata
import sqlite3

import config


def _normalizar(texto):
    """minúsculas + sin acentos."""
    t = unicodedata.normalize("NFD", str(texto))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t.lower().strip()


def _construir_catalogo():
    """
    Devuelve lista de (alias_normalizado, alias_para_filtro) ordenada por
    longitud descendente. 'alias_para_filtro' es el texto que se usará en el
    LIKE de la consulta SQL (un nombre que exista tal cual en la columna).
    """
    con = sqlite3.connect(config.DB_PATH)
    municipios = [
        r[0] for r in con.execute(
            "SELECT DISTINCT municipio FROM eventos WHERE municipio IS NOT NULL"
        ).fetchall()
    ]
    con.close()

    alias = {}  # alias_norm -> alias_filtro
    for valor in municipios:
        # separar municipios compuestos por ';'
        for parte in str(valor).split(";"):
            parte = parte.strip()
            if not parte:
                continue
            # cada lado de '/' es un nombre buscable (bilingüe)
            lados = [p.strip() for p in parte.split("/") if p.strip()]
            for lado in lados:
                clave = _normalizar(lado)
                if len(clave) >= 4:  # evita alias demasiado cortos/ambiguos
                    # guardamos el lado original como término de filtro
                    alias.setdefault(clave, lado)

    # ordenar por longitud del alias (más largo primero)
    catalogo = sorted(alias.items(), key=lambda kv: len(kv[0]), reverse=True)
    return catalogo


# alias coloquiales -> término de filtro que SÍ existe en la columna municipio
_ALIAS_MANUALES = {
    "donosti": "Donostia",
    "gasteiz": "Vitoria-Gasteiz",
    "vitoria": "Vitoria-Gasteiz",
}


# se construye una sola vez al importar
_CATALOGO = _construir_catalogo()
# añadir alias manuales (se reordena por longitud)
for _k, _v in _ALIAS_MANUALES.items():
    _CATALOGO.append((_normalizar(_k), _v))
_CATALOGO.sort(key=lambda kv: len(kv[0]), reverse=True)


def extraer_municipio(texto):
    """
    Busca un municipio dentro del texto libre.
    Devuelve (municipio_para_filtro, texto_sin_municipio) o (None, texto).
    Solo detecta el primer (más largo) municipio encontrado.
    """
    if not texto:
        return None, texto

    texto_norm = _normalizar(texto)

    for alias_norm, alias_filtro in _CATALOGO:
        # coincidencia por palabra completa (límites \b)
        patron = r"\b" + re.escape(alias_norm) + r"\b"
        if re.search(patron, texto_norm):
            # quitar el alias del texto original (insensible a acentos/mayúsc.)
            texto_limpio = _quitar_alias(texto, alias_norm)
            return alias_filtro, texto_limpio

    return None, texto


def _quitar_alias(texto_original, alias_norm):
    """Elimina del texto original la porción que coincide con el alias."""
    palabras = texto_original.split()
    n = len(alias_norm.split())
    resultado, i = [], 0
    while i < len(palabras):
        ventana = " ".join(palabras[i:i + n])
        if _normalizar(ventana) == alias_norm:
            i += n  # saltar las palabras del municipio
        else:
            resultado.append(palabras[i])
            i += 1
    # limpiar preposiciones colgantes al final ("restaurante en" -> "restaurante")
    limpio = " ".join(resultado).strip()
    limpio = re.sub(r"\b(en|de|del|cerca|por)\b\s*$", "", limpio,
                    flags=re.IGNORECASE).strip()
    return limpio
