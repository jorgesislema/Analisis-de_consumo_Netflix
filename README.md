# Análisis de Consumo Netflix 🎬📊

Este proyecto analiza los datos de uso de Netflix provenientes de un usuario, con el objetivo de realizar un estudio profundo sobre patrones de consumo, intereses y comportamientos de visualización. El dashboard interactivo creado con Power BI permite explorar estos datos de manera visual e intuitiva, ofreciendo insights valiosos sobre hábitos de consumo de contenido streaming.

[![GitHub stars](https://img.shields.io/github/stars/tuusuario/Analisis-de_consumo_Netflix?style=social)](https://github.com/tuusuario/Analisis-de_consumo_Netflix/stargazers)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## 🖼️ Vista Previa del Dashboard

A continuación puedes ver una muestra de las distintas páginas del dashboard interactivo desarrollado en Power BI:

### Hoja 1: KPI Tiempo de Visualización
![Hoja 1](https://github.com/jorgesislema/Analisis-de_consumo_Netflix/blob/main/power_bi/hoja1.jpg?raw=true)

### Hoja 2: Calidad Promedio según Usuarios (TMDb)
![Hoja 2](https://github.com/jorgesislema/Analisis-de_consumo_Netflix/blob/main/power_bi/hoja2.jpg?raw=true)

### Hoja 3: Visualización por Día, Mes y Votos
![Hoja 3](https://github.com/jorgesislema/Analisis-de_consumo_Netflix/blob/main/power_bi/hoja3.jpg?raw=true)

### Hoja 4: Medición de Géneros
![Hoja 4](https://github.com/jorgesislema/Analisis-de_consumo_Netflix/blob/main/power_bi/hoja4.jpg?raw=true)

### Hoja 5: Nube de Géneros y Conclusiones
![Hoja 5](https://github.com/jorgesislema/Analisis-de_consumo_Netflix/blob/main/power_bi/hoja5.jpg?raw=true)

---

## 📥 Descargar el Dashboard Interactivo (.pbix)

Puedes descargar el archivo completo del dashboard de Power BI aquí:

👉 [**Descargar Analisis_Netflix.pbix**](https://github.com/jorgesislema/Analisis-de_consumo_Netflix/blob/main/power_bi/Analisis_Netflix.pbix?raw=true)

> Contiene todas las visualizaciones, relaciones de datos y medidas DAX utilizadas en el análisis.
## 🌟 ¿Te gusta este proyecto?

Si encuentras útil este proyecto para analizar tus propios datos de Netflix o aprender sobre análisis de datos, ¡regálanos una estrella en GitHub! Tu apoyo nos motiva a seguir mejorando.

## ✨ Características

- Análisis de calidad del contenido visualizado (calificaciones, popularidad)
- Patrones temporales de consumo (por mes, día, hora)
- Análisis de géneros preferidos con visualizaciones tipo radar ("caracol")
- Visualización de datos con gráficos interactivos y filtros dinámicos
- Dashboard profesional con colores temáticos de Netflix (rojo #E50914, negro #141414, blanco #FFFFFF)
- Integracion con The Movie Database (TMDB) API para enriquecer los datos

## 🛠️ Requisitos

- Python 3.8+
- Power BI Desktop
- API Key de The Movie Database (TMDb)

## 📦 Instalación

1. Clona este repositorio
2. Crea un archivo `.env` en la raíz del proyecto con tu API key:
```
TMDB_API_KEY=tu_api_key_aquí
TMDB_API_READ_ACCESS_TOKEN=tu_token_aquí
```
3. Instala las dependencias:
```
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

- `data/`: Carpetas para datos crudos y procesados
- `notebooks/`: Jupyter notebooks con análisis exploratorio y enriquecimiento de datos
- `scripts/`: Scripts para automatizar el proceso ETL y preparación de datos
- `tableau/`: Archivo PBIX para el dashboard de análisis
- `dashboard_app/`: Archivos del dashboard de Dash (alternativa a Power BI)

## 🚀 Uso

1. Coloca tu historial de Netflix (`NetflixViewingHistory.csv`) en la carpeta `data/raw/`
2. Ejecuta el script ETL para enriquecer los datos:
```
python scripts/run_etl.py
```
3. Prepara los datos para Power BI:
```
python scripts/powerbi_prep.py
```
O simplemente ejecuta el archivo batch:
```
prepare_for_powerbi.bat
```
4. Abre el archivo `tableau/Analisis_Netflix.pbix` en Power BI Desktop para ver el dashboard interactivo

## 🔍 Integración con The Movie Database (TMDB)

Este proyecto aprovecha la potente API de [The Movie Database (TMDB)](https://www.themoviedb.org/) para enriquecer los datos básicos de visualización de Netflix con información detallada sobre cada título, incluyendo:

- **Metadatos completos**: Títulos oficiales, fechas de estreno, duración
- **Calificaciones y popularidad**: Valoraciones medias, número de votos, índice de popularidad
- **Categorización**: Géneros, tipo de contenido (película/serie)
- **Contexto adicional**: Información de producción, datos originales de los títulos

El proceso de enriquecimiento funciona de la siguiente manera:

1. **Extracción**: Se obtiene el historial básico de visualización de Netflix (títulos y fechas)
2. **Limpieza**: Se procesan los títulos para optimizar la búsqueda en la API
3. **Enriquecimiento**: Se consulta la API de TMDB para cada título único usando el endpoint `search/multi`
4. **Detalles**: Se obtienen datos detallados usando los endpoints específicos (`movie/{id}` o `tv/{id}`)
5. **Transformación**: Se procesa toda la información para generar un conjunto de datos enriquecido
6. **Carga**: Se exportan los datos en formato compatible con Power BI

Para utilizar la API de TMDB en este proyecto:
1. Regístrate en [TMDB](https://www.themoviedb.org/signup)
2. Obtén una API key en [configuración de API](https://www.themoviedb.org/settings/api)
3. Añade tu API key al archivo `.env` como se indica en la sección de instalación

> **Nota**: Este proyecto utiliza la API de TMDB con fines educativos y de análisis personal. Asegúrate de cumplir con los [términos de uso](https://www.themoviedb.org/terms-of-use) de TMDB.

## 📊 Análisis y Visualizaciones

El dashboard incluye cinco páginas de análisis interactivo:

1. **KPIs principales**: Resumen general de consumo y estadísticas clave
2. **Análisis de calidad**: Exploración de calificaciones y popularidad del contenido
3. **Análisis temporal**: Patrones de visualización por fecha, hora y temporada
4. **Análisis de géneros**: Preferencias por género con gráficos tipo radar ("caracol")
5. **Recomendaciones**: Conclusiones y sugerencias basadas en los patrones identificados

Cada visualización es interactiva, permitiendo filtrar y profundizar en los datos para descubrir insights personalizados.

## 📝 Licencia

Este proyecto está bajo licencia MIT - ver archivo [LICENSE](LICENSE) para más detalles.

---

### 🌟 ¿Te ha resultado útil este proyecto?

Si te ha gustado este análisis o lo has utilizado como referencia, ¡considera darle una estrella en GitHub! Además, nos encantaría ver tus propias implementaciones o mejoras - no dudes en hacer un fork y compartir tus resultados.
