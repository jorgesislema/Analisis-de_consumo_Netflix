import dash
from dash import html

from pages.pagina_inicio import crear_layout_inicio
from pages.pagina_calidad import crear_layout_calidad
from pages.pagina_tiempo import crear_layout_tiempo
from pages.pagina_generos import crear_layout_generos
from pages.pagina_conclusiones import crear_layout_conclusiones

def router(pathname):
    """
    Gestiona las rutas del dashboard y devuelve el layout correspondiente.
    
    Args:
        pathname: Ruta URL actual
    
    Returns:
        Layout correspondiente a la ruta
    """
    # Página de inicio
    if pathname == "/" or pathname == "":
        return crear_layout_inicio()
    
    # Página de análisis de calidad
    elif pathname == "/calidad":
        return crear_layout_calidad()
    
    # Página de análisis temporal
    elif pathname == "/tiempo":
        return crear_layout_tiempo()
    
    # Página de análisis de géneros
    elif pathname == "/generos":
        return crear_layout_generos()
    
    # Página de conclusiones
    elif pathname == "/conclusiones":
        return crear_layout_conclusiones()
    
    # Página no encontrada (404)
    else:
        return html.Div([
            html.H1("404: Página no encontrada", className="text-danger text-center"),
            html.Hr(),
            html.P(f"La ruta '{pathname}' no existe en este dashboard.", className="text-center"),
            html.Div(
                html.A("Volver al Inicio", href="/", className="btn btn-primary"),
                className="text-center mt-4"
            )
        ], className="container py-5")
