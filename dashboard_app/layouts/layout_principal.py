import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from utils.navbar import crear_navbar

def crear_layout_principal():
    """
    Crea el layout principal del dashboard con sistema de navegación entre páginas.
    Usa los colores de Netflix: rojo (#E50914), negro (#141414) y blanco (#FFFFFF).
    
    Returns:
        html.Div: Layout principal con navegación y contenedor para páginas
    """
    # Definir layout con Navbar y contenedor para las páginas
    layout = html.Div([
        # Almacenar la URL actual
        dcc.Location(id='url', refresh=False),
        
        # Barra de navegación 
        crear_navbar(),
        
        # Banner de Netflix
        html.Div([
            html.Div([
                html.Img(src='/assets/netflix_logo.png', height='60px',
                         style={'margin-right': '20px'}),
                html.H3('Analytics Dashboard', style={'color': '#FFFFFF', 'margin': 0}),
            ], className='d-flex align-items-center'),
            
            html.P('Análisis interactivo de patrones de visualización', 
                   style={'color': '#DDDDDD', 'margin-top': '10px'})
        ], className='container py-4', style={'background-color': '#141414'}),
        
        # Información rápida - Stats generales (nuevos)
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.H4("Total Visualizaciones", className="card-title text-center", 
                               style={'color': '#FFFFFF', 'font-size': '1.2rem'}),
                        html.H2(id="total-visualizaciones", className="text-center",
                               style={'color': '#E50914', 'font-weight': 'bold'})
                    ], style={'background-color': '#222222', 'border': 'none', 'border-left': '4px solid #E50914'}, 
                    className="p-3 h-100")
                ], width=12, md=3, className="mb-4"),
                
                dbc.Col([
                    dbc.Card([
                        html.H4("Calif. Promedio", className="card-title text-center", 
                               style={'color': '#FFFFFF', 'font-size': '1.2rem'}),
                        html.H2(id="calificacion-promedio", className="text-center",
                               style={'color': '#E50914', 'font-weight': 'bold'})
                    ], style={'background-color': '#222222', 'border': 'none', 'border-left': '4px solid #E50914'},
                    className="p-3 h-100")
                ], width=12, md=3, className="mb-4"),
                
                dbc.Col([
                    dbc.Card([
                        html.H4("Series vs Películas", className="card-title text-center", 
                               style={'color': '#FFFFFF', 'font-size': '1.2rem'}),
                        html.H2(id="ratio-series-peliculas", className="text-center",
                               style={'color': '#E50914', 'font-weight': 'bold'})
                    ], style={'background-color': '#222222', 'border': 'none', 'border-left': '4px solid #E50914'},
                    className="p-3 h-100")
                ], width=12, md=3, className="mb-4"),
                
                dbc.Col([
                    dbc.Card([
                        html.H4("Género Principal", className="card-title text-center", 
                               style={'color': '#FFFFFF', 'font-size': '1.2rem'}),
                        html.H2(id="genero-principal", className="text-center",
                               style={'color': '#E50914', 'font-weight': 'bold'})
                    ], style={'background-color': '#222222', 'border': 'none', 'border-left': '4px solid #E50914'},
                    className="p-3 h-100")
                ], width=12, md=3, className="mb-4"),
            ], className="mx-3 mb-4")
        ], id="quick-stats", className="container-fluid d-none"),
        
        # Contenedor para las páginas
        html.Div(id='page-content', className='container-fluid py-4', 
                 style={'background-color': '#141414', 'color': '#FFFFFF', 'min-height': '85vh'}),
        
        # Footer
        html.Footer(
            html.Div([
                html.Hr(style={'border-color': '#333333'}),
                
                # Contenido del footer con información del proyecto
                html.Div([
                    html.Div([
                        html.H5('NETFLIX ANALYTICS', style={'color': '#E50914', 'font-weight': 'bold'}),
                        html.P('Dashboard Interactivo para análisis de consumo de contenidos', 
                               style={'color': '#AAAAAA'})
                    ], className='col-md-6'),
                    
                    html.Div([
                        html.H5('INFORMACIÓN', style={'color': '#E50914', 'font-weight': 'bold'}),
                        html.P([
                            '© 2025 - Dashboard desarrollado con ',
                            html.A('Dash', href='https://dash.plotly.com/', 
                                   style={'color': '#E50914', 'text-decoration': 'none'})
                        ], style={'color': '#AAAAAA'})
                    ], className='col-md-6')
                ], className='row')
            ], className='container')
        , style={'background-color': '#0C0C0C', 'padding': '20px 0'})
    ], style={'background-color': '#141414'})
    
    return layout
