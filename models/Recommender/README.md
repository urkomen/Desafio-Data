# Recomendador de planes (API Flask)

Recomendador por similitud coseno sobre embeddings precalculados
(`intfloat/multilingual-e5-large`, 1024 dims).

## Flujo
1. El usuario envía `id_user`, `consulta` (texto libre del buscador) y `filtros`.
2. **Filtros duros**: se reduce el pool de eventos por los flags `es_*`
   (carrito, cambiador, interior, accesible, mascota) y por `price` (gratis).
   Vienen solo de lo que el usuario marca; la familia NO activa filtros.
   No hay filtro de municipio: la ubicación va dentro del texto de `consulta`.
3. Se construye un **prompt enriquecido** con la consulta + perfil familiar
   (edades + mascota, leídos de SQL) + historial ponderado por rating.
4. Se calcula el **vector de perfil**: media ponderada de los embeddings del
   historial con rating >= 4 y de los favoritos (rating implícito 5).
5. **Score** = α·sim(consulta) + β·sim(perfil) − penalización_temporal.
   α/β dependen del tamaño del historial.

## Estructura
- `config.py`       — rutas, modelo, mapeo filtro→columna
- `data_access.py`  — SQLite + carga de embeddings (.npy + índice)
- `recommender.py`  — prompt, perfil, scoring
- `app.py`          — API Flask

## Ejecutar
```bash
pip install -r requirements.txt
python app.py          # carga modelo (2GB la 1ª vez) y levanta en :5000
```

## Ejemplo
La ubicación (si la hay) va dentro del texto libre de `consulta`;
no hay filtro duro por municipio. Filtros: carrito, cambiador, interior,
accesible, mascota, gratis.

```bash
curl -X POST http://localhost:5000/recomendar \
  -H "Content-Type: application/json" \
  -d '{"id_user":10,
       "consulta":"Museo Bilbao planes en familia",
       "filtros":{"carrito":true,"interior":true,"mascota":true,"gratis":false}}'
```
