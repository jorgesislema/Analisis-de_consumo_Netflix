import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from layouts.layout_principal import crear_layout_principal
from utils.router import router

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
    Input('url', 'pathname')
)
def display_page(pathname):
    return router(pathname)

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

if __name__ == "__main__":
    app.run_server(debug=True)
