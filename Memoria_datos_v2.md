**Memoria Técnica del Proyecto: Buscador de Eventos en Euskadi para Familias**

1. Introducción y Objetivos del Proyecto
   El objetivo principal de este proyecto es el diseño e implementación de una plataforma unificada de búsqueda y recomendación de eventos, actividades culturales, recursos gastronómicos y espacios naturales orientados específicamente al público infantil y familiar dentro de la Comunidad Autónoma del País Vasco (Euskadi).

Debido a la dispersión de la información en múltiples portales institucionales, agendas locales y servicios meteorológicos, se ha desarrollado una solución de ingeniería de datos capaz de integrar, unificar y estructurar estas fuentes fragmentadas. El resultado final permite a las familias planificar actividades de ocio basándose en la tipología del evento, la localización geográfica precisa, la valoración de otros usuarios y las condiciones climatológicas previstas en tiempo real en el municipio de destino.

2. Arquitectura de Datos y Fuentes de Información
   El ecosistema de datos del proyecto combina repositorios de datos abiertos gubernamentales con servicios comerciales globales mediante un enfoque híbrido:

* Open Data Euskadi (Eventos y Ocio): Repositorio central de la administración pública para la extracción de la agenda cultural oficial y catálogos de recursos recreativos.
* Kulturklik: Portal especializado en la difusión de la cultura vasca, utilizado para obtener flujos dinámicos de eventos en vivo.

* Catálogo de Hostelería de Euskadi: Base de datos de restaurantes, asadores, sidrerías y bares de pintxos idóneos para la planificación de comidas familiares.
* Buscador de Espacios Naturales Protegidos (Ingurumena): Extracción de entornos naturales, rutas e itinerarios ecológicos aptos para niños.

* Euskalmet (Agencia Vasca de Meteorología): Incorporación de previsiones meteorológicas y alertas climáticas en tiempo real vinculadas a cada municipio.
* API de Mapas B5M (Diputación Foral de Gipuzkoa): Capas cartográficas de alta definición y validación geoespacial del territorio.

* Ticketmaster Discovery API & SerpApi (Google Local Results): Componentes globales utilizados para capturar macroeventos musicales/teatrales y recolectar de forma estructurada las opiniones, puntuaciones y horarios reales de los comercios directamente desde los motores de búsqueda.

3. Proceso de Obtención de Archivos CSV a partir de Páginas Web
   La primera fase de la infraestructura de datos consistió en la captura, extracción y estructuración de la información web en archivos planos de formato CSV (Comma-Separated Values). Dado el origen y la tecnología heterogénea de los portales de origen, se aplicaron dos metodologías diferenciadas:


![1780656154295](image/Memoria_datos_v2/1780656154295.png)


Estructuración en Tablas de Memoria y Volcado a CSV: Los datos crudos —ya limpios de etiquetas HTML, scripts o estilos CSS— se ordenan en una matriz bidimensional de filas y columnas. Finalmente, se exportan localmente a archivos .csv configurados bajo la codificación UTF-8 para garantizar la correcta visualización de caracteres especiales como tildes, diéresis y eñes, utilizando delimitadores estándar (como la coma o el punto y coma).


3.1. Consumo de Endpoints Públicos y Almacenamiento Intermedio
Para los portales que disponían de servicios de datos abiertos estructurados (como los endpoints de Open Data Euskadi y Kulturklik), el proceso se agilizó sustancialmente:

Se realizaron llamadas de consulta apuntando a los endpoints específicos (como el flujo de eventos culturales).

Se configuraron los parámetros de cabecera requeridos, inyectando la clave de autenticación X-API-Key en los portales que así lo exigían.

Debido a las restricciones de paginación (un máximo de 100 registros por consulta), se implementó un bucle incremental basado en parámetros de desplazamiento (offset) y límites (limit) para descargar el histórico y la agenda futura de forma completa.

Las respuestas nativas recibidas en formatos estructurados como JSON y JSON-LD se "aplanaron" de forma relacional, convirtiendo los objetos y arreglos anidados en tablas bidimensionales aptas para guardarse directamente como archivos CSV intermedios.

4. Transformación de Datos y Creación del Modelo SQL
   Una vez que todas las fuentes de información se consolidaron de manera homogénea en archivos CSV, se inició la fase de ingeniería e inserción en una base de datos relacional (SQL). Este paso es indispensable para permitir búsquedas cruzadas complejas (por ejemplo, filtrar eventos infantiles en un municipio concreto que además cuenten con restaurantes cercanos con alta valoración y buen clima).

![1780656119379](image/Memoria_datos_v2/1780656119379.png)

4.1. Diseño del Modelo Entidad-Relación
Se estructuró una base de datos normalizada para evitar redundancias y optimizar los tiempos de respuesta del buscador familiar. Las principales entidades definidas son:

MUNICIPIOS: Catálogo oficial de localidades del País Vasco, incluyendo códigos postales y la provincia correspondiente (Álava, Bizkaia, Gipuzkoa). Actúa como eje central de conexión. (Clave Primaria: ID_Municipio).

EVENTOS: Agenda consolidada de actividades familiares extraídas de Open Data, Kulturklik y Ticketmaster. (Clave Primaria: ID_Evento / Clave Foránea: ID_Municipio).

HOSTELERÍA: Restaurantes, asadores y bares de pintxos aptos para familias, enriquecidos con datos de SerpApi. (Clave Primaria: ID_Establecimiento / Clave Foránea: ID_Municipio).

ESPACIOS_NATURALES: Parques, rutas y áreas recreativas protegidas procedentes del buscador de Ingurumena. (Clave Primaria: ID_Espacio / Clave Foránea: ID_Municipio).

METEOROLOGÍA: Predicciones diarias y alertas climáticas vinculadas a cada municipio de la red de Euskalmet. (Clave Primaria: ID_Prediccion / Clave Foránea: ID_Municipio).

4.2. Flujo de Carga de Datos (De CSV a Tablas SQL)
La migración y poblamiento de la base de datos a partir de los archivos CSV se realizó mediante un proceso de ETL (Extract, Transform, Load):

Creación del Esquema (DDL): Se redactaron y ejecutaron sentencias SQL de tipo CREATE TABLE especificando con precisión los tipos de datos para cada columna: números enteros para identificadores, cadenas de texto de longitud variable (VARCHAR) para títulos y descripciones, formatos DATE o TIMESTAMP para los días de los eventos, y valores de punto flotante (FLOAT) para las coordenadas de latitud y longitud. Se declararon de forma explícita las restricciones de integridad referencial (claves primarias y foráneas).

Limpieza y Normalización de Datos: Antes de la inserción, los datos contenidos en los CSV pasaron por una etapa de curación:

Estandarización de Municipios: Se unificaron los nombres de las localidades (por ejemplo, asegurando que variantes como "Donostia-San Sebastián", "San Sebastián" o "Donostia" apuntasen exactamente al mismo registro y código en la tabla de Municipios).

Depuración de Valores Nulos: Se eliminaron filas con campos críticos vacíos (como eventos sin fecha o restaurantes sin coordenadas geográficas) y se transformaron las cadenas de texto que representaban puntuaciones o precios en formatos numéricos operables.

Inserción Masiva (DML): Utilizando comandos de carga optimizados (como instrucciones de importación masiva o scripts secuenciales de sentencias INSERT INTO), los registros limpios procedentes de los CSV se inyectaron directamente en el motor SQL de destino.

Indexación para Búsqueda Familiar: Para garantizar que el buscador web funcione con agilidad frente a múltiples usuarios concurrentes, se crearon índices SQL sobre las columnas más consultadas: las fechas de los eventos, las categorías de actividades de ocio y los identificadores geográficos de los municipios.

5. Conclusión
   A través de esta metodología, el proyecto ha logrado transformar millones de líneas de código HTML amorfo y decenas de respuestas JSON independientes en un almacén de datos SQL perfectamente estructurado, relacional y optimizado. El sistema cuenta ahora con una base de datos sólida que permite ejecutar consultas complejas de manera inmediata, sentando los cimientos técnicos óptimos para el desarrollo de la interfaz de usuario y los algoritmos de recomendación inteligente de planes familiares.
