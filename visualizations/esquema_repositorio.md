Analisis-de_consumo_Netflix/   # Directorio raíz de tu proyecto
│
├── .github/workflows/         # (Opcional avanzado) Para automatización con GitHub Actions
│   └── python-lint.yaml       #   (ej. revisar calidad de código automáticamente)
│
├── data/                      # Carpeta para todos los datos
│   ├── raw/                   # Datos originales, sin modificar. ¡Nunca edites estos!
│   │   ├── NetflixViewingHistory.csv
│   │   └── data sett octopusteam nexflix.csv
│   ├── interim/               # Archivos de datos temporales o intermedios (resultado de pasos ETL)
│   │   └── viewing_history_cleaned.csv
│   └── processed/             # Datos finales, limpios y enriquecidos, listos para el análisis y Tableau
│       └── netflix_viewing_enriched.csv
│
├── docs/                      # (Opcional) Documentación adicional: diccionario de datos, notas, etc.
│   └── data_dictionary.md
│
├── notebooks/                 # Jupyter Notebooks: ideales para exploración, pruebas y EDA
│   ├── 01_Data_Loading_and_Cleaning.ipynb
│   ├── 02_API_Enrichment_Tests.ipynb # Para probar llamadas a la API
│   └── 03_Exploratory_Data_Analysis.ipynb
│
├── scripts/                   # Scripts de Python (.py) para código reutilizable o automatizado
│   ├── etl/                   # Scripts dedicados al proceso de Extracción, Transformación y Carga
│   │   ├── __init__.py        # Hace que 'etl' sea un paquete Python
│   │   ├── tmdb_api_fetcher.py # Funciones para obtener datos de TMDb API
│   │   ├── data_processor.py  # Funciones para limpiar y transformar los datos
│   │   └── run_etl.py         # Script principal que ejecuta todo el proceso ETL
│   └── utils/                 # (Opcional) Funciones de utilidad usadas en varios sitios
│       └── __init__.py
│
├── tableau/                   # Archivos relacionados con Tableau
│   ├── datasources/           # (Opcional) Puedes guardar aquí archivos .tds (definición fuente datos)
│   └── workbooks/             # Guarda aquí tus libros de trabajo de Tableau (.twb)
│       └── Netflix_Analysis_Dashboard.twb # .twb es mejor para Git que .twbx (que incluye datos)
│
├── visualizations/            # (Opcional) Para guardar gráficos estáticos generados (PNG, JPG...)
│   └── top_genres_watched.png
│
# --- Archivos Clave en la Raíz ---
│
├── .env                       # **IMPORTANTE:** Almacena aquí tu API Key de TMDb.
│                              #   **¡Asegúrate de añadir este archivo a .gitignore!**
│                              #   Ejemplo dentro: TMDB_API_KEY='tu_clave_aqui'
│
├── .gitignore                 # Archivo MUY importante. Define qué archivos/carpetas Git debe ignorar.
│                              #   Debe incluir: .env, venv/, __pycache__/, *.pyc, .DS_Store,
│                              #   quizás data/processed/* o data/interim/* si son muy grandes,
│                              #   y posiblemente *.twbx si usas ese formato y es pesado.
│
├── LICENSE                    # Especifica cómo otros pueden usar tu código (Ej. MIT License).
│
├── README.md                  # El archivo más importante. Explica qué hace el proyecto,
│                              #   cómo instalarlo (requirements), cómo ejecutarlo,
│                              #   un resumen de los hallazgos y un enlace a tu dashboard público.
│
└── requirements.txt           # Lista de las librerías de Python necesarias.
                               #   Se genera con `pip freeze > requirements.txt`
                               #   Permite a otros instalar dependencias con `pip install -r requirements.txt`