import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from utils.navbar import crear_navbar

def crear_layout_principal():
    """
    Crea el layout principal del dashboard con sistema de navegación entre páginas.
    Usa los colores de Netflix: rojo (#E50914), negro (#141414) y blanco (#FFFFFF).
    """
    # Definir layout con Navbar y contenedor para las páginas
    layout = html.Div([
        # Almacenar la URL actual
        dcc.Location(id='url', refresh=False),
        
        # Barra de navegación 
        crear_navbar(),
        
        # Contenedor para las páginas
        html.Div(id='page-content', className='container-fluid py-4', 
                 style={'background-color': '#141414', 'color': '#FFFFFF', 'min-height': '85vh'}),
        
        # Footer
        html.Footer(
            html.Div([
                html.Hr(style={'border-color': '#333333'}),
                html.P('NETFLIX ANALYTICS - Dashboard Interactivo © 2025', 
                       className='text-center', style={'color': '#E50914', 'font-weight': 'bold'})
            ], className='container')
        )
    ], style={'background-color': '#141414'})
    
    return layout
