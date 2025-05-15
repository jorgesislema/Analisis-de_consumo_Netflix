import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from layouts.layout_principal import crear_layout_principal
from utils.router import router
from utils.data_utils import cargar_datos
import pandas as pd

# Inicializar la aplicación Dash con tema Bootstrap (DARKLY para el tema oscuro de Netflix)
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,  # Tema oscuro para simular Netflix
        dbc.icons.FONT_AWESOME
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    suppress_callback_exceptions=True
)

app.title = "Netflix Analytics Dashboard"

# Definir el layout principal con navegación
app.layout = crear_layout_principal()

# Callback para gestionar la navegación entre páginas
@app.callback(
    Output('page-content', 'children'),
    Output('quick-stats', 'className'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # Verificar si estamos en la página de inicio para mostrar u ocultar las estadísticas rápidas
    quick_stats_class = "container-fluid" if pathname == "/" else "container-fluid d-none"
    return router(pathname), quick_stats_class

# Callback para el toggle del navbar en dispositivos móviles
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [dash.State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Callbacks para estadísticas rápidas
@app.callback(
    [Output('total-visualizaciones', 'children'),
     Output('calificacion-promedio', 'children'),
     Output('ratio-series-peliculas', 'children'),
     Output('genero-principal', 'children')],
    [Input('url', 'pathname')]
)
def actualizar_estadisticas_rapidas(pathname):
    try:
        # Cargar datos
        df = cargar_datos()
        
        # Calcular estadísticas
        total_visualizaciones = len(df)
        calificacion_promedio = round(df['Calificacion_Promedio_TMDb'].mean(), 1)
        
        # Calcular ratio de series vs películas
        series = df['Tipo_Medio_TMDb'].value_counts().get('tv', 0)
        peliculas = df['Tipo_Medio_TMDb'].value_counts().get('movie', 0)
        ratio = f"{series} / {peliculas}"
        
        # Obtener género principal
        # Primero expandir todos los géneros
        generos_expandidos = []
        for _, row in df.iterrows():
            if pd.notna(row['Generos_TMDb']) and isinstance(row['Generos_TMDb'], str):
                for genero in row['Generos_TMDb'].split(','):
                    genero = genero.strip()
                    if genero:
                        generos_expandidos.append(genero)
        
        # Contar y obtener el más común
        if generos_expandidos:
            from collections import Counter
            genero_principal = Counter(generos_expandidos).most_common(1)[0][0]
        else:
            genero_principal = "No disponible"
            
        return total_visualizaciones, calificacion_promedio, ratio, genero_principal
    
    except Exception as e:
        print(f"Error al calcular estadísticas: {e}")
        return "N/A", "N/A", "N/A", "N/A"

if __name__ == "__main__":
    app.run_server(debug=True)
