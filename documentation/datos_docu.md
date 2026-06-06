# Datos del Sistema

Repositorio centralizado de todos los datos del proyecto: eventos, usuarios, familias, embeddings precalculados y configuraciones.

---

**Última actualización**: Junio 2026

**Versión de esquema**: 2.0

## Historial de Cambios

| Fecha      | Cambio                                  | Versión |
| ---------- | --------------------------------------- | -------- |
| 2026-06-02 | Descarga inicial de eventos             | 1.0      |
| 2026-06-05 | Agregadas tablas de usuarios y familias | 2.0      |
| 2026-06-06 | Embeddings generados                    | 2.0      |

---

## Tabla de Contenidos

- [Historial de Cambios](#historial-de-cambios)
- [Descripción General](#descripción-general)
- [Estructura de Carpetas](#estructura-de-carpetas)
- [Datos en CSV](#datos-en-csv)
- [Base de Datos SQLite](#base-de-datos-sqlite)
- [Embeddings Precalculados](#embeddings-precalculados)
- [Esquema de Datos](#esquema-de-datos)
- [Relaciones Entre Tablas](#relaciones-entre-tablas)
- [Estadísticas](#estadísticas)
- [Guía de Actualización](#guía-de-actualización)
- [Consultas Útiles](#consultas-útiles)
- [Consideraciones de Privacidad](#consideraciones-de-privacidad)
- [Referencias](#referencias)

---

## Descripción General

Este directorio contiene toda la información necesaria para el funcionamiento de los sistemas de recomendación y chatbot:

### Componentes Principales

| Componente           | Tipo                     | Propósito                                                   |
| -------------------- | ------------------------ | ------------------------------------------------------------ |
| **CSVs**       | Archivos planos          | Datos de eventos, usuarios, familias (respaldo + auditoría) |
| **SQLite**     | Base de datos relacional | Almacenamiento principal de datos                            |
| **Embeddings** | Vectores numéricos      | Representación semántica de eventos (1024 dimensiones)     |

### Flujo de Datos

```
APIs Públicas (Euskadi, Kulturklik, etc.)
        ↓
    Descarga (Python script)
        ↓
    Limpieza y Transformación
        ↓
    CSV (descargas/)
        ↓
    Carga a SQLite (eventos.db)
        ↓
    Generación de Embeddings
        ↓
    Embedding Store (embeddings.npy + índice)
```

---

## Estructura de Carpetas

```
data/
├── descargas/                  # Datos en formato CSV (respaldo)
│   ├── events_2026-06-02.csv  # Eventos culturales
│   ├── families.csv            # Perfiles de familias
│   ├── family_members.csv      # Miembros de cada familia
│   ├── users.csv               # Cuentas de usuarios
│   ├── user_favorite_events.csv # Eventos marcados como favoritos
│   └── user_selected_recommendations.csv # Historial de clics
│
├── embeddings/                 # Vectores precalculados
│   ├── embeddings.npy         # Matriz de embeddings (float32)
│   └── embeddings_index.csv   # Mapeo id_evento → índice de fila
│
├── eventos.db                  # Base de datos SQLite principal
│
└── README.md                   # Este archivo
```

---

## Datos en CSV

### 1. `events_2026-06-02.csv`

**Descripción**: Eventos culturales del País Vasco.

**Delimitador**: `;` (punto y coma)

**Campos principales**:

| Campo               | Tipo  | Descripción                          | Ejemplo                                          |
| ------------------- | ----- | ------------------------------------- | ------------------------------------------------ |
| `business_id`     | INT   | ID del negocio/organizador (opcional) | 1245                                             |
| `fuente`          | STR   | URL de la fuente original             | `https://turismoa.euskadi.eus/...`             |
| `external_id`     | STR   | ID en sistema externo                 | `evt_98765`                                    |
| `title`           | STR   | Nombre del evento                     | `Festival de Jazz de Vitoria`                  |
| `description`     | STR   | Descripción detallada                | `Festival anual de jazz...`                    |
| `categoria`       | STR   | Categoría del evento                 | `Música`, `Exposición`, `Teatro`         |
| `tipo_plantilla`  | STR   | Tipo de lugar                         | `Centros comerciales`, `Museos`, `Teatros` |
| `municipio`       | STR   | Ciudad/municipio                      | `Vitoria-Gasteiz`                              |
| `territorio`      | STR   | Región (Álava/Bizkaia/Gipuzkoa)     | `araba`, `bizkaia`, `gipuzkoa`             |
| `address`         | STR   | Dirección completa                   | `Calle Principal, 42`                          |
| `lat`             | FLOAT | Latitud de geolocalización           | 42.8449                                          |
| `lng`             | FLOAT | Longitud                              | -2.6691                                          |
| `telefono`        | STR   | Número de contacto                   | `945 146 096`                                  |
| `email`           | STR   | Email de contacto                     | `info@evento.com`                              |
| `website`         | STR   | Sitio web oficial                     | `https://evento.com`                           |
| `es_interior`     | BOOL  | ¿Actividad en interior?              | `True`, `False`                              |
| `es_carrito`      | BOOL  | ¿Accesible con carrito de bebé?     | `True`, `False`                              |
| `es_cambiador`    | BOOL  | ¿Hay zona de cambio?                 | `True`, `False`                              |
| `es_silla_ruedas` | BOOL  | ¿Accesible para sillas de ruedas?    | `True`, `False`                              |
| `es_mascotas`     | BOOL  | ¿Se permiten mascotas?               | `True`, `False`                              |
| `edad_minima`     | INT   | Edad mínima recomendada              | 0, 6, 12, 18                                     |
| `fecha_inicio`    | DATE  | Fecha de inicio del evento            | `2026-06-15`                                   |
| `fecha_fin`       | DATE  | Fecha de fin                          | `2026-06-20`                                   |
| `lugar`           | STR   | Lugar específico (ej: Sala A)        | `Sala Conciertos Principal`                    |
| `price`           | FLOAT | Precio en € (0 = gratis)             | 0, 15.5, 50                                      |
| `imagen_url`      | STR   | URL de imagen promocional             | `https://cdn.ejemplo.com/img.jpg`              |
| `tipo_evento`     | STR   | Clasificación adicional              | `concierto`, `exposicion`, `taller`        |

**Registros aproximados**: 500+

**Último actualizado**: 2026-06-02

**Ejemplo de fila**:

```
;https://turismoa.euskadi.eus/es/museos/guggenheim/...;;Guggenheim Bilbao;Museo de arte moderno y contemporáneo;Música;Museos;Bilbao;bizkaia;Avenida Abandoibarra, 2;43.3949;-2.9351;944 358 000;info@guggenheim.es;www.guggenheimbildao.com;True;True;True;True;False;0;2026-06-01;2026-12-31;Sala Puente;13;https://...;
```

---

### 2. `users.csv`

**Descripción**: Cuentas de usuario en el sistema.

**Campos**:

| Campo        | Tipo | Descripción                                  |
| ------------ | ---- | --------------------------------------------- |
| `id`       | INT  | Identificador único del usuario              |
| `email`    | STR  | Correo electrónico (único)                  |
| `password` | STR  | Hash de contraseña (enmascarado en ejemplos) |
| `role`     | STR  | Rol del usuario (`user`, `admin`)         |

**Registros aproximados**: 100+

**Ejemplo**:

```
1;iker1@email.com;PassIker2024!;user
2;amaia2@email.com;PassAmaia2024!;user
```

---

### 3. `families.csv`

**Descripción**: Perfiles de familias registradas en el sistema.

**Campos**:

| Campo           | Tipo | Descripción                     |
| --------------- | ---- | -------------------------------- |
| `id`          | INT  | Identificador único de familia  |
| `user_id`     | INT  | FK a usuarios (relación 1:1)    |
| `family_name` | STR  | Nombre descriptivo de la familia |

**Registros aproximados**: 100+

**Ejemplo**:

```
1;10;Familia Etxebarria-Aguirre
2;11;Familia Garrido-López
```

---

### 4. `family_members.csv`

**Descripción**: Miembros individuales de cada familia.

**Campos**:

| Campo         | Tipo | Descripción                    | Ejemplo                       |
| ------------- | ---- | ------------------------------- | ----------------------------- |
| `id`        | INT  | ID único del miembro           | 1                             |
| `family_id` | INT  | FK a families                   | 1                             |
| `nombre`    | STR  | Nombre del miembro              | `Iker`                      |
| `edad`      | INT  | Edad en años                   | 8                             |
| `rol`       | STR  | `adulto`, `niño`, `bebe` | `niño`                     |
| `mascota`   | STR  | Mascota (NULL si no hay)        | `perro`, `gato`, `NULL` |

**Registros aproximados**: 300+

**Ejemplo**:

```
1;1;Iker (adulto);42;adulto;gato
2;1;Amaia (adulta);40;adulto;gato
3;1;Jon (niño);8;niño;NULL
4;1;Miren (niña);5;niño;NULL
```

---

### 5. `user_favorite_events.csv`

**Descripción**: Eventos marcados como favoritos por usuarios.

**Campos**:

| Campo              | Tipo     | Descripción                    |
| ------------------ | -------- | ------------------------------- |
| `id`             | INT      | ID de la relación              |
| `user_id`        | INT      | FK a usuarios                   |
| `event_id`       | INT      | FK a eventos                    |
| `fecha_guardado` | DATETIME | Cuándo se marcó como favorito |

**Registros aproximados**: 50+

---

### 6. `user_selected_recommendations.csv`

**Descripción**: Historial de eventos que el usuario visitó o interaccionó con.

**Campos**:

| Campo                 | Tipo     | Descripción                          |
| --------------------- | -------- | ------------------------------------- |
| `id`                | INT      | ID del registro                       |
| `user_id`           | INT      | FK a usuarios                         |
| `event_id`          | INT      | FK a eventos                          |
| `rating`            | INT      | Valoración 1-5 (NULL si no evaluado) |
| `fecha_evento`      | DATE     | Cuándo fue el evento                 |
| `fecha_interaccion` | DATETIME | Cuándo interactuó el usuario        |
| `notas`             | STR      | Comentarios del usuario               |

**Registros aproximados**: 200+

**Uso**: Este tabla alimenta el recomendador para construir el perfil del usuario.

---

## Base de Datos SQLite

### Ubicación

```
data/eventos.db
```

### Descripción

Base de datos relacional que almacena toda la información de forma normalizada. Los CSVs se cargan aquí para consultas rápidas.

### Tablas Principales

#### 1. `events`

Eventos culturales completos.

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    business_id INTEGER,
    external_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    categoria TEXT,
    tipo_plantilla TEXT,
    municipio TEXT,
    territorio TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    telefono TEXT,
    email TEXT,
    website TEXT,
    es_interior BOOLEAN,
    es_carrito BOOLEAN,
    es_cambiador BOOLEAN,
    es_silla_ruedas BOOLEAN,
    es_mascotas BOOLEAN,
    edad_minima INTEGER,
    fecha_inicio DATE,
    fecha_fin DATE,
    lugar TEXT,
    price REAL,
    imagen_url TEXT,
    tipo_evento TEXT,
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `users`

Cuentas de usuario.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `families`

Perfiles familiares.

```sql
CREATE TABLE families (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    family_name TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 4. `family_members`

Miembros de familias.

```sql
CREATE TABLE family_members (
    id INTEGER PRIMARY KEY,
    family_id INTEGER NOT NULL,
    nombre TEXT,
    edad INTEGER,
    rol TEXT, -- 'adulto', 'niño', 'bebe'
    mascota TEXT,
    FOREIGN KEY (family_id) REFERENCES families(id)
);
```

#### 5. `user_events`

Historial de eventos visitados/recomendados.

```sql
CREATE TABLE user_events (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    rating INTEGER, -- 1-5 stars
    fecha_evento DATE,
    fecha_interaccion DATETIME,
    notas TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

#### 6. `user_favorites`

Eventos favoritos.

```sql
CREATE TABLE user_favorites (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    fecha_guardado DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE(user_id, event_id)
);
```

### Cómo Acceder

```bash
# Instalar SQLite CLI (si no lo tienes)
# Windows: descargar desde sqlite.org
# Mac: brew install sqlite
# Linux: apt-get install sqlite3

# Abrir la BD
sqlite3 data/eventos.db

# Queries útiles dentro de sqlite3
.tables                           # Ver todas las tablas
.schema events                    # Ver estructura de tabla
SELECT COUNT(*) FROM events;      # Contar eventos
SELECT * FROM events LIMIT 5;     # Ver primeros 5 eventos
```

---

## Embeddings Precalculados

### Descripción

Vectores numéricos de 1024 dimensiones que representan el significado semántico de cada evento. Se usan para calcular similaridad entre eventos/consultas.

### Archivos

#### 1. `embeddings.npy`

**Formato**: NumPy binary format (.npy)

**Dimensiones**: (N, 1024) donde N = número de eventos

**Tipo de dato**: float32

**Normalización**: Vectores normalizados (norma ≈ 1.0)

**Tamaño**: ~2 GB

**Descripción**:

- Fila i contiene el embedding del evento cuyo ID está en `embeddings_index.csv` fila i
- Similitud coseno = producto escalar (vectores normalizados)
- Generado con modelo: `intfloat/multilingual-e5-large`

**Cómo cargar**:

```python
import numpy as np
import pandas as pd

# Cargar embeddings
embeddings_matrix = np.load('data/embeddings/embeddings.npy')
print(f"Forma: {embeddings_matrix.shape}")  # (500, 1024)

# Cargar índice
index_df = pd.read_csv('data/embeddings/embeddings_index.csv')
id_to_row = dict(zip(index_df['id'], index_df['row_idx']))

# Obtener embedding de evento específico
event_id = 1234
row_idx = id_to_row[event_id]
embedding = embeddings_matrix[row_idx]  # Array de 1024 floats
```

#### 2. `embeddings_index.csv`

**Descripción**: Mapeo de IDs de evento a índices de fila en embeddings.npy

**Campos**:

| Campo       | Tipo | Descripción                      |
| ----------- | ---- | --------------------------------- |
| `id`      | INT  | ID del evento (PK en events)      |
| `row_idx` | INT  | Índice de fila en embeddings.npy |

**Registros**: Mismo número que eventos (500+)

**Ejemplo**:

```
id,row_idx
1234,0
5678,1
9999,2
...
```

**¿Por qué es necesario?**

- Robustez ante cambios de orden
- Mapeo O(1) entre ID evento y vector
- Facilita auditoría

### Generación de Embeddings

Para regenerar los embeddings (si cambias eventos):

```bash
cd notebooks
jupyter notebook embedder_multilingual_e5.ipynb
# Seguir las instrucciones del notebook
```

---

## Esquema de Datos

### Diagrama ER

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │
│ email       │
│ password    │
│ role        │
└──────┬──────┘
       │
       │ 1:1
       │
┌──────▼──────┐       ┌──────────────────┐
│  families   │◄─────►│  family_members  │
├─────────────┤ 1:N   ├──────────────────┤
│ id (PK)     │       │ id (PK)          │
│ user_id (FK)│       │ family_id (FK)   │
│ family_name │       │ nombre           │
└─────────────┘       │ edad             │
                      │ rol              │
                      │ mascota          │
                      └──────────────────┘

┌──────────────┐      ┌─────────────────┐
│   events     │◄─────┤ user_favorites  │
├──────────────┤ N:M  ├─────────────────┤
│ id (PK)      │      │ id (PK)         │
│ title        │      │ user_id (FK)    │
│ municipio    │      │ event_id (FK)   │
│ price        │      │ fecha_guardado  │
│ es_carrito   │      └─────────────────┘
│ ...          │
└──────┬───────┘      ┌──────────────────┐
       │              │  user_events     │
       └─────────────►├──────────────────┤
         N:M          │ id (PK)          │
                      │ user_id (FK)     │
                      │ event_id (FK)    │
                      │ rating (1-5)     │
                      │ fecha_evento     │
                      │ fecha_interaccion│
                      │ notas            │
                      └──────────────────┘
```

---

## Relaciones Entre Tablas

### Flujo de Datos

**Usuario registra su familia:**

```
users (id: 10)
  → families (user_id: 10)
    → family_members (family_id: 1, edad: 8, rol: 'niño')
```

**Usuario interactúa con eventos:**

```
users (id: 10)
  → user_events (user_id: 10, event_id: 1234, rating: 5)
  → events (id: 1234, title: 'Museo', price: 13)
```

**Usuario marca favoritos:**

```
users (id: 10)
  → user_favorites (user_id: 10, event_id: 1234)
  → events (id: 1234)
```

### Integridad Referencial

- Todas las FKs están definidas
- Restricción UNIQUE en user_favorites (evita duplicados)
- Cascada de eliminaciones (ON DELETE CASCADE) en desarrollo

---

## Estadísticas

| Métrica                    | Valor  | Fecha      |
| --------------------------- | ------ | ---------- |
| Total eventos               | ~500   | 2026-06-02 |
| Eventos en Bilbao           | ~80    | 2026-06-02 |
| Eventos gratuitos           | ~150   | 2026-06-02 |
| Usuarios registrados        | ~100   | 2026-06-06 |
| Familias registradas        | ~100   | 2026-06-06 |
| Miembros de familia total   | ~300   | 2026-06-06 |
| Interacciones (user_events) | ~200   | 2026-06-06 |
| Embeddings generados        | ~500   | 2026-06-02 |
| Tamaño BD SQLite           | ~50 MB | 2026-06-06 |
| Tamaño embeddings.npy      | ~2 GB  | 2026-06-02 |

---

## Guía de Actualización

### Ciclo de Actualización

```
Semanal - lunes (Manual o Automático)
├── 02:00 → Descarga eventos de APIs (script Python)
├── 02:15 → Limpieza y transformación
├── 02:30 → Generación de CSV en descargas/
├── 03:00 → Carga a SQLite
└── Regeneración de embeddings
```

### Actualizar Eventos desde APIs

```bash
cd scripts
python fetch_events.py  # Script de descarga (no incluido, necesita implementación)
```

### Actualizar Embeddings

```bash
cd notebooks
# Ejecutar embedder_multilingual_e5.ipynb
# O desde línea de comandos:
python -c "from scripts.embedding import generate_embeddings; generate_embeddings()"
```

### Hacer Backup

```bash
# Backup de datos
cp -r data/ data_backup_2026-06-06/

# O usar script de respaldo automático
python scripts/backup.py
```

---

## Consultas Útiles

### SQL

```sql
-- Eventos gratuitos en Bilbao
SELECT title, municipio, fecha_inicio FROM events
WHERE municipio = 'Bilbao' AND price = 0;

-- Top 10 eventos con más favoritos
SELECT e.title, COUNT(f.id) as favoritos
FROM events e
LEFT JOIN user_favorites f ON e.id = f.event_id
GROUP BY e.id
ORDER BY favoritos DESC
LIMIT 10;

-- Perfil de usuario (familia + historial)
SELECT u.email, 
       COUNT(DISTINCT fm.id) as num_miembros,
       COUNT(DISTINCT ue.id) as num_eventos_visitados
FROM users u
LEFT JOIN families f ON u.id = f.user_id
LEFT JOIN family_members fm ON f.id = fm.family_id
LEFT JOIN user_events ue ON u.id = ue.user_id
WHERE u.id = 10
GROUP BY u.id;

-- Eventos recomendados para usuario (basado en historial con rating >= 4)
SELECT DISTINCT e.* FROM events e
WHERE e.id IN (
    SELECT DISTINCT event_id FROM user_events 
    WHERE user_id = 10 AND rating >= 4
)
LIMIT 10;
```

### Python (Pandas)

```python
import pandas as pd
import sqlite3

# Cargar desde CSV
df_events = pd.read_csv('data/descargas/events_2026-06-02.csv', sep=';')

# Cargar desde SQLite
conn = sqlite3.connect('data/eventos.db')
df_events = pd.read_sql_query("SELECT * FROM events", conn)

# Análisis
print(df_events['municipio'].value_counts())  # Eventos por municipio
print(df_events['price'].describe())           # Estadísticas de precios
print(df_events['es_carrito'].sum())           # Eventos con carrito
```

---

## Consideraciones de Privacidad

### Datos Sensibles

**El archivo `users.csv` contiene:**

- Correos electrónicos
- Contraseñas (hash)
- Roles

**Medidas implementadas (producción):**

- No incluir en repositorio público (agregar a .gitignore)
- Acceso restringido en entornos de producción
- Usar variables de entorno para credenciales

!!!!! Los datos actuales de las tablas de usuario son FICTICIOS, están para poder realizar pruebas

### RGPD

Para solicitudes de datos/eliminación de usuarios:

1. Identificar usuario en tabla `users`
2. Eliminar en cascada:
   - `user_events`
   - `user_favorites`
   - `family_members`
   - `families`
   - `users`

```sql
DELETE FROM users WHERE id = 10;  -- Cascada automática si está configurada
```

---

## Referencias

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [NumPy .npy Format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html)
- [Pandas CSV Reading](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [Sentence Transformers E5 Model](https://huggingface.co/intfloat/multilingual-e5-large)
