# Dashboard Interactivo de Análisis de Netflix

Este dashboard interactivo ofrece un análisis detallado de los patrones de consumo en Netflix, basado en datos procesados del historial de visualización.

## Características principales

El dashboard consta de 5 páginas con análisis detallado:

1. **Página de Inicio**: Resumen general con KPIs y métricas principales
2. **Análisis de Calidad**: Exploración de calificaciones, géneros mejor valorados y relación calidad-popularidad
3. **Análisis Temporal**: Patrones de visualización por día, hora, semana, mes y año
4. **Análisis de Géneros**: Distribución de géneros, combinaciones frecuentes y evolución temporal con gráficos "caracol" (radar)
5. **Conclusiones y Recomendaciones**: Insights principales y recomendaciones personalizadas

Cada página incluye 6-7 visualizaciones interactivas que responden a la interacción del usuario, con funciones de filtrado y destacado.

## Cómo ejecutar el dashboard

### Método 1: Usando el script de ejecución

1. Navega a la carpeta del dashboard
2. Ejecuta el archivo `run_dashboard.bat` (Windows)

### Método 2: Ejecución manual

1. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

2. Ejecuta la aplicación:
   ```
   python app.py
   ```

3. Abre el navegador en http://localhost:8050

## Requisitos

- Python 3.8 o superior
- Navegador web moderno (Chrome, Firefox, Edge)
- Conexión a Internet para cargar componentes de Bootstrap

## Estructura del proyecto

```
dashboard_app/
│
├── app.py                # Punto de entrada principal
├── requirements.txt      # Dependencias del proyecto
├── run_dashboard.bat     # Script para ejecutar el dashboard
│
├── assets/               # Archivos estáticos (CSS, imágenes)
│   └── styles.css
│
├── layouts/              # Definiciones de layouts
│   └── layout_principal.py
│
├── pages/                # Páginas del dashboard
│   ├── pagina_inicio.py
│   ├── pagina_calidad.py
│   ├── pagina_tiempo.py
│   ├── pagina_generos.py
│   └── pagina_conclusiones.py
│
└── utils/                # Utilidades y funciones helper
    ├── data_utils.py
    ├── navbar.py
    └── router.py
```

## Notas importantes

- El dashboard está diseñado para ser responsivo y funcionar en dispositivos móviles y de escritorio
- Se han sustituido los gráficos de pastel por alternativas más profesionales como gráficos Sunburst y de radar
- Todas las visualizaciones incluyen interactividad al pasar el cursor y hacer clic en elementos

---

Desarrollado para el análisis detallado de patrones de consumo en Netflix, 2023
