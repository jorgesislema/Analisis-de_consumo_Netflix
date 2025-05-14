import pandas as pd
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

from utils.data_utils import cargar_datos, crear_grafico_barras, crear_grafico_linea, crear_mapa_calor

def crear_layout_tiempo():
    """
    Crea el layout para la página de análisis temporal.
    
    Returns:
        Layout de Dash con los componentes de la página de análisis temporal
    """
    # Cargar datos
    df = cargar_datos()
    
    # Verificar si se cargaron correctamente los datos
    if df.empty:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-danger text-center"),
            html.P("No se pudieron cargar los datos para el análisis temporal.", className="text-center")
        ])
    
    # Calcular rango de fechas
    fecha_inicio = df['Fecha_Visualizacion'].min()
    fecha_fin = df['Fecha_Visualizacion'].max()
    
    # 1. Gráfico de visualizaciones por mes/año
    vis_mensual = df.groupby(['Anio', 'Mes_Num']).size().reset_index(name='Visualizaciones')
    vis_mensual['Fecha'] = pd.to_datetime(vis_mensual['Anio'].astype(str) + '-' + vis_mensual['Mes_Num'].astype(str) + '-01')
    vis_mensual = vis_mensual.sort_values('Fecha')
    
    fig_mensual = crear_grafico_linea(
        vis_mensual,
        'Fecha',
        'Visualizaciones',
        'Visualizaciones Mensuales',
        tipo_linea='markers+lines'
    )
    
    fig_mensual.update_layout(
        xaxis_title="Mes/Año",
        yaxis_title="Número de Visualizaciones",
        xaxis=dict(
            tickformat="%b %Y",
            tickangle=45
        )
    )
    
    # 2. Gráfico de visualizaciones por día de la semana
    vis_dia_semana = df['Dia_Semana'].value_counts().reset_index()
    vis_dia_semana.columns = ['Día de la Semana', 'Visualizaciones']
    
    # Ordenar días de la semana correctamente
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    vis_dia_semana['Día de la Semana'] = pd.Categorical(vis_dia_semana['Día de la Semana'], categories=dias_orden, ordered=True)
    vis_dia_semana = vis_dia_semana.sort_values('Día de la Semana')
    
    fig_dia_semana = crear_grafico_barras(
        vis_dia_semana,
        'Día de la Semana',
        'Visualizaciones',
        'Visualizaciones por Día de la Semana',
        color_col='Visualizaciones'
    )
    
    # 3. Gráfico de visualizaciones por hora del día
    vis_hora = df['Hora'].value_counts().reset_index()
    vis_hora.columns = ['Hora', 'Visualizaciones']
    vis_hora = vis_hora.sort_values('Hora')
    
    fig_hora = crear_grafico_barras(
        vis_hora,
        'Hora',
        'Visualizaciones',
        'Visualizaciones por Hora del Día',
        color_col='Visualizaciones'
    )
    
    fig_hora.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,
            tickangle=0
        )
    )
    
    # 4. Mapa de calor de día de la semana vs hora
    fig_heatmap = crear_mapa_calor(
        df,
        'Hora',
        'Dia_Semana',
        'Titulo_Original_Netflix',
        'Patrón de Visualización por Día y Hora'
    )
    
    # 5. Visualizaciones por mes del año (independiente del año)
    vis_mes = df['Mes'].value_counts().reset_index()
    vis_mes.columns = ['Mes', 'Visualizaciones']
    
    # Ordenar meses correctamente
    meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    vis_mes['Mes'] = pd.Categorical(vis_mes['Mes'], categories=meses_orden, ordered=True)
    vis_mes = vis_mes.sort_values('Mes')
    
    fig_mes = crear_grafico_barras(
        vis_mes,
        'Mes',
        'Visualizaciones',
        'Visualizaciones por Mes del Año',
        color_col='Visualizaciones'
    )
    
    # 6. Tiempo desde el estreno hasta la visualización
    df_tiempo_estreno = df[df['Tiempo_Desde_Estreno'].notna() & (df['Tiempo_Desde_Estreno'] >= 0)].copy()
    
    # Crear categorías de tiempo desde estreno
    bins = [-1, 7, 30, 90, 180, 365, float('inf')]
    labels = ['1 semana', '1 mes', '3 meses', '6 meses', '1 año', 'Más de 1 año']
    df_tiempo_estreno['Categoria_Tiempo'] = pd.cut(df_tiempo_estreno['Tiempo_Desde_Estreno'], bins=bins, labels=labels)
    
    tiempo_estreno = df_tiempo_estreno['Categoria_Tiempo'].value_counts().reset_index()
    tiempo_estreno.columns = ['Tiempo desde Estreno', 'Visualizaciones']
    
    # Ordenar categorías
    tiempo_estreno['Tiempo desde Estreno'] = pd.Categorical(
        tiempo_estreno['Tiempo desde Estreno'], 
        categories=labels, 
        ordered=True
    )
    tiempo_estreno = tiempo_estreno.sort_values('Tiempo desde Estreno')
    
    fig_tiempo_estreno = crear_grafico_barras(
        tiempo_estreno,
        'Tiempo desde Estreno',
        'Visualizaciones',
        'Tiempo desde el Estreno hasta la Visualización',
        color_col='Visualizaciones'
    )
    
    # 7. Comparativa de patrones de visualización: Series vs Películas
    # Agrupar por hora y tipo
    vis_hora_tipo = df.groupby(['Hora', 'Tipo_Medio_TMDb']).size().reset_index(name='Visualizaciones')
    vis_hora_tipo['Tipo'] = vis_hora_tipo['Tipo_Medio_TMDb'].map({'tv': 'Series', 'movie': 'Películas'})
    
    fig_hora_tipo = px.line(
        vis_hora_tipo, 
        x='Hora', 
        y='Visualizaciones',
        color='Tipo',
        title='Patrones de Visualización por Hora: Series vs Películas',
        markers=True,
        color_discrete_map={'Series': '#3366CC', 'Películas': '#FF9900'},
        template="plotly_white"
    )
    
    fig_hora_tipo.update_layout(
        xaxis_title="Hora del Día",
        yaxis_title="Número de Visualizaciones",
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1
        ),
        legend_title="Tipo de Contenido",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Crear layout con todos los elementos
    layout = html.Div([
        # Título y descripción
        html.Div([
            html.H1([
                html.I(className="fas fa-clock me-2"),
                "Análisis Temporal de Visualizaciones"
            ], className="display-4 text-primary text-center mb-3"),
            html.P(
                "Exploración detallada de los patrones temporales de consumo de contenido en Netflix.",
                className="lead text-center mb-4"
            ),
            html.Hr(),
        ], className="my-4"),
        
        # Filtros interactivos
        html.Div([
            dbc.Card([
                dbc.CardHeader("Filtros de Análisis Temporal", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Rango de Fechas"),
                            dcc.DatePickerRange(
                                id='filtro-fechas',
                                min_date_allowed=fecha_inicio.date(),
                                max_date_allowed=fecha_fin.date(),
                                start_date=fecha_inicio.date(),
                                end_date=fecha_fin.date(),
                                display_format='DD/MM/YYYY'
                            )
                        ], width=12, md=6),
                        
                        dbc.Col([
                            html.Label("Tipo de Contenido"),
                            dcc.Dropdown(
                                id='filtro-tipo-tiempo',
                                options=[
                                    {'label': 'Todos', 'value': 'todos'},
                                    {'label': 'Series', 'value': 'tv'},
                                    {'label': 'Películas', 'value': 'movie'}
                                ],
                                value='todos',
                                clearable=False
                            )
                        ], width=12, md=6),
                    ]),
                    
                    html.Div(id='contenedor-filtros-tiempo-aplicados', className="mt-3")
                ])
            ], className="mb-4")
        ]),
        
        # Resumen del período
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H3("Resumen del Período Analizado", className="card-title"),
                    html.Div([
                        html.Div([
                            html.H4(f"{fecha_inicio.strftime('%d/%m/%Y')}", className="text-primary"),
                            html.P("Fecha Inicial", className="text-muted")
                        ], className="text-center"),
                        
                        html.Div([
                            html.H4(f"{fecha_fin.strftime('%d/%m/%Y')}", className="text-primary"),
                            html.P("Fecha Final", className="text-muted")
                        ], className="text-center"),
                        
                        html.Div([
                            html.H4(f"{(fecha_fin - fecha_inicio).days}", className="text-primary"),
                            html.P("Días Totales", className="text-muted")
                        ], className="text-center"),
                        
                        html.Div([
                            html.H4(f"{len(df):,}", className="text-primary"),
                            html.P("Visualizaciones", className="text-muted")
                        ], className="text-center")
                    ], className="d-flex justify-content-around")
                ], body=True, className="mb-4")
            ], width=12),
        ]),
        
        # Primera fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Tendencia Mensual de Visualizaciones", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-tendencia-mensual',
                            figure=fig_mensual,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        # Segunda fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visualizaciones por Día de la Semana", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-dia-semana',
                            figure=fig_dia_semana,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visualizaciones por Mes del Año", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-mes',
                            figure=fig_mes,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
        ]),
        
        # Tercera fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visualizaciones por Hora del Día", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-hora',
                            figure=fig_hora,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Patrones por Tipo de Contenido", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-hora-tipo',
                            figure=fig_hora_tipo,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
        ]),
        
        # Cuarta fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Mapa de Calor: Día vs Hora", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-heatmap',
                            figure=fig_heatmap,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Tiempo desde el Estreno", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-tiempo-estreno',
                            figure=fig_tiempo_estreno,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
        ]),
        
        # Nota informativa
        dbc.Alert([
            html.H4("Interpretación del Análisis Temporal", className="alert-heading"),
            html.P([
                "Los patrones temporales de visualización pueden revelar información valiosa sobre sus hábitos de consumo:",
                html.Ul([
                    html.Li("Identifique sus días y horas de mayor actividad"),
                    html.Li("Observe si hay tendencias estacionales en su consumo"),
                    html.Li("Analice si prefiere contenido reciente o más antiguo")
                ])
            ]),
            html.Hr(),
            html.P(
                "Utilice los filtros para delimitar períodos específicos y compare patrones entre series y películas.",
                className="mb-0"
            )
        ], color="info", className="mt-3")
    ])
    
    return layout
