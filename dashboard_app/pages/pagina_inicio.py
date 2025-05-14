from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

from utils.data_utils import cargar_datos, crear_grafico_indicadores, crear_grafico_barras, crear_mapa_calor, crear_grafico_linea

def crear_layout_inicio():
    """
    Crea el layout para la página de inicio del dashboard.
    
    Returns:
        Layout de Dash con los componentes de la página de inicio
    """
    # Cargar datos
    df = cargar_datos()
    
    # Verificar si se cargaron correctamente los datos
    if df.empty:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-danger text-center"),
            html.P("No se pudieron cargar los datos para el dashboard.", className="text-center")
        ])
    
    # Calcular métricas generales para los KPIs
    total_visualizaciones = len(df)
    periodo_inicio = df['Fecha_Visualizacion'].min().strftime('%d-%m-%Y')
    periodo_fin = df['Fecha_Visualizacion'].max().strftime('%d-%m-%Y')
    total_series = df[df['Es_Serie']]['Titulo_TMDb'].nunique()
    total_peliculas = df[df['Es_Pelicula']]['Titulo_TMDb'].nunique()
    total_dias = (df['Fecha_Visualizacion'].max() - df['Fecha_Visualizacion'].min()).days
    promedio_diario = round(total_visualizaciones / total_dias, 1) if total_dias > 0 else 0
    
    # Calcular distribución series vs películas
    tipo_conteo = df['Tipo_Medio_TMDb'].value_counts().reset_index()
    tipo_conteo.columns = ['Tipo', 'Conteo']
    tipo_conteo['Tipo'] = tipo_conteo['Tipo'].map({'tv': 'Series', 'movie': 'Películas'})
    
    # Preparar gráficos para la página de inicio
    # 1. Gráfico de distribución series vs películas (sunburst en vez de pie chart)
    fig_distribucion = px.sunburst(
        tipo_conteo, 
        path=['Tipo'], 
        values='Conteo',
        title='Distribución: Series vs Películas',
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="plotly_white"
    )
    
    fig_distribucion.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(size=14)
    )
    
    # 2. Gráfico de actividad por día de la semana
    vis_por_dia = df['Dia_Semana'].value_counts().reset_index()
    vis_por_dia.columns = ['Día', 'Visualizaciones']
    
    # Ordenar días de la semana correctamente
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    vis_por_dia['Día'] = pd.Categorical(vis_por_dia['Día'], categories=dias_orden, ordered=True)
    vis_por_dia = vis_por_dia.sort_values('Día')
    
    fig_dia_semana = crear_grafico_barras(
        vis_por_dia,
        'Día',
        'Visualizaciones',
        'Actividad por Día de la Semana',
        color_col='Visualizaciones'
    )
    
    # 3. Tendencia de visualizaciones a lo largo del tiempo
    vis_temporal = df.groupby(['Anio', 'Mes_Num']).size().reset_index(name='Visualizaciones')
    vis_temporal['Fecha'] = pd.to_datetime(vis_temporal['Anio'].astype(str) + '-' + vis_temporal['Mes_Num'].astype(str) + '-01')
    vis_temporal = vis_temporal.sort_values('Fecha')
    
    fig_tendencia = crear_grafico_linea(
        vis_temporal,
        'Fecha',
        'Visualizaciones',
        'Tendencia de Visualizaciones a lo Largo del Tiempo'
    )
    
    # 4. Top 10 series y películas
    series_df = df[(df['Es_Serie']) & (df['Titulo_TMDb'].notna())]
    top_series = series_df['Titulo_TMDb'].value_counts().reset_index().head(10)
    top_series.columns = ['Serie', 'Episodios Vistos']
    
    peliculas_df = df[(df['Es_Pelicula']) & (df['Titulo_TMDb'].notna())]
    top_peliculas = peliculas_df['Titulo_TMDb'].value_counts().reset_index().head(10)
    top_peliculas.columns = ['Película', 'Veces Vista']
    
    fig_top_series = crear_grafico_barras(
        top_series[::-1],
        'Episodios Vistos',
        'Serie',
        'Top 10 Series Más Vistas',
        orientacion='h',
        color_col='Episodios Vistos'
    )
    
    fig_top_peliculas = crear_grafico_barras(
        top_peliculas[::-1],
        'Veces Vista',
        'Película',
        'Top 10 Películas Más Vistas',
        orientacion='h',
        color_col='Veces Vista'
    )
    
    # 5. Mapa de calor de visualizaciones por día y hora
    if 'Hora' in df.columns:
        fig_heatmap = crear_mapa_calor(
            df,
            'Hora',
            'Dia_Semana',
            'Titulo_Original_Netflix',
            'Patrón de Visualización por Día y Hora'
        )
    else:
        fig_heatmap = go.Figure()
        fig_heatmap.update_layout(
            title="No hay datos de hora disponibles para crear el mapa de calor",
            template="plotly_white"
        )
    
    # Crear layout con todos los elementos
    layout = html.Div([
        # Título y descripción
        html.Div([
            html.H1([
                html.I(className="fas fa-chart-line me-2"),
                "Dashboard de Análisis de Consumo de Netflix"
            ], className="display-4 text-primary text-center mb-3"),
            html.P(
                "Análisis interactivo de patrones de visualización, preferencias y hábitos de consumo en Netflix.",
                className="lead text-center mb-4"
            ),
            html.Hr(),
        ], className="my-4"),
        
        # KPIs principales
        html.Div([
            html.H3("Métricas Principales", className="text-center mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.H1(f"{total_visualizaciones:,}", className="text-center text-primary"),
                        html.P("Total Visualizaciones", className="text-center text-muted")
                    ], body=True, className="border-primary mb-3 h-100")
                ], width=12, md=3),
                
                dbc.Col([
                    dbc.Card([
                        html.H1(f"{total_dias:,}", className="text-center text-primary"),
                        html.P(f"Días Analizados ({periodo_inicio} - {periodo_fin})", className="text-center text-muted")
                    ], body=True, className="border-primary mb-3 h-100")
                ], width=12, md=3),
                
                dbc.Col([
                    dbc.Card([
                        html.H1(f"{promedio_diario}", className="text-center text-primary"),
                        html.P("Visualizaciones Diarias", className="text-center text-muted")
                    ], body=True, className="border-primary mb-3 h-100")
                ], width=12, md=3),
                
                dbc.Col([
                    dbc.Card([
                        html.H1(f"{total_series:,} / {total_peliculas:,}", className="text-center text-primary"),
                        html.P("Series / Películas Únicas", className="text-center text-muted")
                    ], body=True, className="border-primary mb-3 h-100")
                ], width=12, md=3),
            ]),
        ], className="mb-5"),
        
        # Gráficos principales
        dbc.Row([
            # Distribución de tipos y actividad semanal
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribución y Actividad", className="bg-primary text-white"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=fig_distribucion, config={'displayModeBar': False})
                            ], width=12, md=5),
                            
                            dbc.Col([
                                dcc.Graph(figure=fig_dia_semana, config={'displayModeBar': False})
                            ], width=12, md=7),
                        ])
                    ])
                ], className="mb-4")
            ], width=12),
            
            # Tendencia temporal
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Evolución Temporal", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(figure=fig_tendencia)
                    ])
                ], className="mb-4")
            ], width=12),
            
            # Series y películas top
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Contenido Más Visto", className="bg-primary text-white"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=fig_top_series)
                            ], width=12, md=6),
                            
                            dbc.Col([
                                dcc.Graph(figure=fig_top_peliculas)
                            ], width=12, md=6),
                        ])
                    ])
                ], className="mb-4")
            ], width=12),
            
            # Mapa de calor
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Patrones de Visualización", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(figure=fig_heatmap)
                    ])
                ], className="mb-4")
            ], width=12),
        ]),
        
        # Nota sobre la navegación del dashboard
        dbc.Alert([
            html.H4("Navegación del Dashboard", className="alert-heading"),
            html.P([
                "Explore las diferentes secciones del dashboard a través del menú superior para un análisis más detallado: ",
                html.Strong("Análisis de Calidad, Análisis Temporal, Análisis de Géneros y Conclusiones.")
            ]),
            html.Hr(),
            html.P(
                "Cada visualización es interactiva. Pase el cursor sobre los elementos gráficos para ver detalles y utilice las opciones de filtro.",
                className="mb-0"
            )
        ], color="info", className="mt-3")
    ])
    
    return layout
