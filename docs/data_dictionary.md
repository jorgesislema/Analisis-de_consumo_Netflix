# Diccionario de Datos: Análisis de Consumo Netflix 📊

Este documento detalla los campos (variables) presentes en los diferentes conjuntos de datos utilizados en el proyecto de análisis de consumo de Netflix. El propósito es proporcionar una referencia completa sobre qué representa cada campo, su tipo de datos, rango de valores, origen, y su uso en el análisis.

## 🎯 Objetivo

Estos conjuntos de datos están diseñados para permitir análisis detallados del consumo personal de Netflix, centrándose en:
- Patrones temporales de visualización (días, horas, meses)
- Preferencias de géneros y tipos de contenido
- Valoración de calidad del contenido según puntuaciones de TMDb
- Tendencias de visualización a lo largo del tiempo

## 📋 Tabla Principal: `netflix_eda_processed.csv`

Este archivo contiene los datos principales enriquecidos del historial de visualización de Netflix, combinando los datos originales de Netflix con información detallada de The Movie Database (TMDb).

| Campo | Tipo | Descripción | Origen | Valores Posibles |
|-------|------|-------------|--------|------------------|
| `Titulo_Original_Netflix` | texto | Título exacto como aparece en el historial de Netflix, incluyendo información de temporada/episodio | Netflix | Cualquier texto |
| `Fecha_Visualizacion` | fecha/hora | Fecha y hora en que se visualizó el contenido | Netflix | Formato: YYYY-MM-DD HH:MM:SS |
| `Titulo_Limpio_Busqueda` | texto | Versión limpia del título utilizada para búsquedas en API, sin información de temporada/episodio | Procesamiento | Cualquier texto |
| `ID_TMDb` | entero | Identificador único del título en The Movie Database | TMDB API | Entero positivo |
| `Titulo_TMDb` | texto | Título oficial según The Movie Database | TMDB API | Cualquier texto |
| `Generos_TMDb` | texto | Lista de géneros separados por comas | TMDB API | Ej: "Drama, Comedy", "Action, Thriller" |
| `Popularidad_TMDb` | decimal | Índice de popularidad (mayor valor = más popular) | TMDB API | Típicamente entre 0-100 |
| `Calificacion_Promedio_TMDb` | decimal | Calificación promedio (0-10) basada en votos de usuarios | TMDB API | 0.0 - 10.0 |
| `Cantidad_Votos_TMDb` | entero | Número total de votos recibidos | TMDB API | Entero positivo |
| `Tipo_Medio_TMDb` | texto | Tipo de contenido | TMDB API | 'movie' (película) o 'tv' (serie) |
| `Fecha_Estreno_TMDb` | fecha | Fecha de estreno original del contenido | TMDB API | Formato: YYYY-MM-DD |
| `Duracion_Minutos_TMDb` | decimal | Duración en minutos (películas) o duración promedio de episodio (series) | TMDB API | Entero positivo |
| `Tipo_Medio` | texto | Versión simplificada de `Tipo_Medio_TMDb` | Procesamiento | 'movie' o 'tv' |
| `Calidad` | texto | Clasificación simplificada de calidad basada en puntuación | Procesamiento | 'Alta', 'Media', 'Baja' |
| `Anio` | entero | Año extraído de `Fecha_Visualizacion` | Procesamiento | Formato: YYYY |
| `Mes_Num` | entero | Número de mes | Procesamiento | 1-12 |
| `Dia_Mes` | entero | Día del mes | Procesamiento | 1-31 |
| `Dia_Semana_Num` | entero | Día de la semana numérico | Procesamiento | 0=Lunes, 6=Domingo |
| `Hora_Visualizacion` | entero | Hora del día | Procesamiento | 0-23 |
| `Semana_Anio` | entero | Número de semana del año (ISO) | Procesamiento | 1-53 |
| `Mes` | texto | Nombre del mes en español | Procesamiento | 'Enero' a 'Diciembre' |
| `Dia_Semana` | texto | Nombre del día de la semana en español | Procesamiento | 'Lunes' a 'Domingo' |
| `Categoria_Calidad` | texto | Clasificación detallada de calidad en 4 niveles | Procesamiento | 'Excelente', 'Bueno', 'Regular', 'Malo' |
| `Es_Serie` | booleano | Indica si el contenido es una serie | Procesamiento | True/False |
| `Es_Pelicula` | booleano | Indica si el contenido es una película | Procesamiento | True/False |
| `Tiempo_Desde_Estreno` | entero | Días transcurridos entre estreno y visualización | Procesamiento | Entero (puede ser negativo) |
| `Tiempo_Visualizacion` | entero | Tiempo estimado de visualización en minutos | Estimación | Entero positivo |

### 📝 Detalles sobre campos calculados:

- **Calidad**: Clasificación basada en `Calificacion_Promedio_TMDb`:
  - `Alta`: ≥ 7.5
  - `Media`: 6.0 - 7.4
  - `Baja`: < 6.0

- **Categoria_Calidad**: Clasificación más detallada:
  - `Excelente`: ≥ 8.0
  - `Bueno`: 7.0 - 7.9
  - `Regular`: 6.0 - 6.9
  - `Malo`: < 6.0

- **Tiempo_Visualizacion**: Estimación basada en la duración del contenido:
  - Para películas: Entre 70-100% de la duración total (`Duracion_Minutos_TMDb`)
  - Para series: Entre 80-100% de la duración del episodio (`Duracion_Minutos_TMDb`)

## 📊 Tablas Derivadas para Análisis

### `promedio_calidad_tipo.csv`

Este archivo contiene el promedio de calificaciones por tipo de medio, facilitando comparaciones rápidas entre la calidad promedio de películas y series.

| Campo | Tipo | Descripción | Valores Posibles |
|-------|------|-------------|------------------|
| `Tipo_Medio_TMDb` | texto | Tipo de contenido | 'movie' o 'tv' |
| `Promedio_Calidad` | decimal | Promedio de `Calificacion_Promedio_TMDb` para ese tipo | 0.0 - 10.0 |

### `resumen_calidad_tipo.csv`

Resume el conteo de títulos por tipo de medio y categoría de calidad, permitiendo análisis de distribución de calidad.

| Campo | Tipo | Descripción | Valores Posibles |
|-------|------|-------------|------------------|
| `Tipo_Medio_TMDb` | texto | Tipo de contenido | 'movie' o 'tv' |
| `Calidad` | texto | Categoría de calidad | 'Alta', 'Media', 'Baja' |
| `Conteo` | entero | Número de títulos en esa combinación | Entero positivo |

### `netflix_analisis_generos.csv`

Versión expandida de los datos con una fila por cada combinación de título y género, permitiendo análisis detallados por género.

| Campo | Tipo | Descripción | Valores Posibles |
|-------|------|-------------|------------------|
| `Genero` | texto | Género individual extraído de `Generos_TMDb` | Ej: 'Drama', 'Comedy', 'Action', etc. |
| `Popularidad_TMDb` | decimal | Índice de popularidad del título | Típicamente entre 0-100 |
| `Calificacion_Promedio_TMDb` | decimal | Calificación promedio del título | 0.0 - 10.0 |
| `Tipo_Medio` | texto | Tipo de contenido | 'movie' o 'tv' |
| `Fecha_Visualizacion` | fecha/hora | Fecha y hora de visualización | Formato: YYYY-MM-DD HH:MM:SS |
| `Anio` | entero | Año de visualización | Formato: YYYY |
| `Titulo_TMDb` | texto | Título del contenido | Cualquier texto |

### `generos_populares.csv`

Agregación de géneros con estadísticas por género, ideal para identificar los géneros más vistos y mejor valorados.

| Campo | Tipo | Descripción | Valores Posibles |
|-------|------|-------------|------------------|
| `Genero` | texto | Nombre del género | Ej: 'Drama', 'Comedy', 'Action', etc. |
| `Popularidad_TMDb` | decimal | Promedio de popularidad para ese género | Típicamente entre 0-100 |
| `Calificacion_Promedio_TMDb` | decimal | Promedio de calificación para ese género | 0.0 - 10.0 |
| `Conteo` | entero | Número de veces que aparece el género | Entero positivo |

## 🔄 Flujo de Procesamiento de Datos

1. Los datos originales se exportan desde Netflix (`NetflixViewingHistory.csv`)
2. Se enriquecen con información de The Movie Database API
3. Se procesan mediante el script `powerbi_prep.py` para:
   - Limpiar y formatear datos
   - Extraer componentes temporales
   - Calcular campos derivados (calidad, tipo, etc.)
   - Generar tablas para análisis específicos

## 📁 Datos Originales: `NetflixViewingHistory.csv`

Archivo original exportado desde la cuenta de Netflix (Cuenta > Perfil > Mi Actividad).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Title` | texto | Título del contenido visto |
| `Date` | fecha | Fecha de visualización |

## 🛠️ Uso en Power BI

Estos conjuntos de datos están específicamente estructurados para facilitar la creación de visualizaciones en Power BI, con campos pensados para diferentes tipos de análisis:

- **Análisis temporal**: Uso de `Anio`, `Mes`, `Dia_Semana`, `Hora_Visualizacion`
- **Análisis de calidad**: Uso de `Calidad`, `Categoria_Calidad`, `Calificacion_Promedio_TMDb`
- **Análisis por tipo**: Uso de `Tipo_Medio`, `Es_Serie`, `Es_Pelicula`
- **Análisis de géneros**: Uso de `netflix_analisis_generos.csv` y `generos_populares.csv`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Title` | texto | Título del contenido visto |
| `Date` | fecha | Fecha de visualización (sin hora) |

---

## Notas adicionales

- **Datos faltantes**: Los campos numéricos pueden contener valores `NaN` o `0` cuando la información no está disponible.
- **Género "Sin género"**: Aparece cuando TMDB no proporciona información de género para un título.
- **Duración de series**: Para series, `Duracion_Minutos_TMDb` representa la duración típica de un episodio, no de la temporada completa.
- **Limitaciones de `Tiempo_Visualizacion`**: Este es un valor estimado, no representa necesariamente el tiempo exacto que el usuario pasó viendo el contenido.

## Uso en Power BI

Cuando trabajes con estos datos en Power BI, considera lo siguiente:

- Utiliza relaciones entre las tablas basadas en los campos comunes como `Tipo_Medio_TMDb` y `Genero`.
- Para análisis temporal, aprovecha la jerarquía de tiempo: Año > Mes > Día.
- Para filtros interactivos, considera usar `Calidad`, `Tipo_Medio` y `Genero` como dimensiones principales.
