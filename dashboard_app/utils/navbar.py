import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

def crear_navbar():
    """
    Crea la barra de navegación del dashboard con estilo Netflix.
    """
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Logo/Título del Dashboard
                dbc.NavbarBrand(
                    [
                        html.I(className="fas fa-play-circle me-2", style={"color": "#E50914"}),
                        "NETFLIX ANALYTICS"
                    ],
                    href="/",
                    className="ms-2 text-netflix"
                ),
                
                # Toggle para modo móvil
                dbc.NavbarToggler(id="navbar-toggler"),
                
                # Elementos de navegación
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("Inicio", href="/")),
                            dbc.NavItem(dbc.NavLink("Análisis de Calidad", href="/calidad")),
                            dbc.NavItem(dbc.NavLink("Análisis Temporal", href="/tiempo")),
                            dbc.NavItem(dbc.NavLink("Análisis de Géneros", href="/generos")),
                            dbc.NavItem(dbc.NavLink("Conclusiones", href="/conclusiones")),
                        ],
                        className="ms-auto",
                        navbar=True
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="#141414",  # Color negro de Netflix
        dark=True,
        className="mb-4",
    )
    
    return navbar
    
    return navbar
