**README: Sistema de Datos de Eventos en Euskadi**

**Descripción**
Se trata de un sistema que recopila automáticamente información sobre eventos (conciertos, exposiciones, festivales, etc.) que ocurren en Euskadi, los organiza y los guarda en una base de datos para poder consultarlos fácilmente.

El Gobierno Vasco y otras entidades publican datos de eventos en internet, pero:

Están dispersos en diferentes webs y APIs
Tienen formatos distintos (unos usan JSON, otros XML, cada uno con sus campos)
No hay un lugar único donde consultarlos todos juntos
Queríamos tener todos esos eventos en un solo sitio, con un formato uniforme, para poder:

-Buscar eventos por fecha, lugar o tipo
-Hacer análisis (¿cuántos eventos hay en Bizkaia? ¿qué meses tienen más actividad?)
-Alimentar otras aplicaciones (webs, apps móviles, chatbots...)

**Funcionamiento**
El proceso tiene cuatro pasos:

APIs públicas  →  Descarga  →  Archivo CSV  →  Base de datos SQL

1. Descarga de datos (Extracción)
   Un script en Python se conecta a las APIs públicas (Open Data Euskadi, Kulturklik...) y descarga los eventos. Es como pedirle a esas webs: "Dame todos los eventos de los próximos 3 meses".
2. Limpieza y organización (Transformación)
   Los datos vienen "sucios": fechas en formatos raros, campos vacíos, duplicados... El script los limpia y los pone todos con la misma estructura.
3. Guardado en CSV (Almacenamiento intermedio)
   Antes de meterlos en la base de datos, los guardamos en un archivo CSV. Esto nos permite:

-Tener un respaldo por si algo falla
-Revisar los datos antes de cargarlos
-Auditar qué se cargó y cuándo

4. Carga en la base de datos (SQL)
   Finalmente, otro script lee el CSV y mete los datos en SQLiteStudio. Si un evento ya existía, lo actualiza; si es nuevo, lo añade.

![captura csv](captura_csv.png)

¿Qué datos guardamos?
De cada evento capturamos:

Campo	Ejemplo
Título	"Festival de Jazz de Vitoria"
Fechas	15-20 julio 2024
Lugar	Vitoria-Gasteiz, Álava
Coordenadas	42.84, -2.67
Categoría	Música
Precio	25€ - 60€
Es gratuito	No
Más info	https://...
Todo está disponible en euskera y castellano cuando la fuente lo proporciona.

**Cada cuánto se actualiza**
El sistema se ejecuta automáticamente cada día a las 6:00 de la mañana. Descarga los eventos de los próximos 90 días, actualiza los que hayan cambiado y añade los nuevos.

**Tecnologías**
Python 3.11 — Para los scripts de extracción y carga
Pandas 2.3.3 — Para manipular y limpiar los datos
SQLiteStudio 3.4.21— Como base de datos
CSV — Como formato intermedio
Estructura del proyecto

****  REVISAR   *********************************************

eventos-euskadi/
├── extractor.py      # Descarga datos de las APIs
├── transformer.py    # Limpia y normaliza
├── loader.py         # Carga en SQL
├── main.py           # Orquesta todo el proceso
├── schema.sql        # Definición de las tablas
├── exports/          # Aquí se guardan los CSV diarios
├── logs/             # Registros de ejecución
└── requirements.txt  # Dependencias Python

Próximos pasos
 Añadir más fuentes de datos (Bilbao Turismo, Donostia Kultura...)
 Crear una API REST para consultar los eventos
 Dashboard con estadísticas
 Notificaciones de nuevos eventos por categoría
