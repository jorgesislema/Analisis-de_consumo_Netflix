import pandas as pd
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from utils.data_utils import cargar_datos, crear_grafico_barras, crear_grafico_linea, crear_grafico_radar

def crear_layout_calidad():
    """
    Crea el layout para la página de análisis de calidad.
    
    Returns:
        Layout de Dash con los componentes de la página de análisis de calidad
    """
    # Cargar datos
    df = cargar_datos()
    
    # Verificar si se cargaron correctamente los datos
    if df.empty:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-danger text-center"),
            html.P("No se pudieron cargar los datos para el análisis de calidad.", className="text-center")
        ])
    
    # Filtrar solo datos con calificación
    df_con_calificacion = df[df['Calificacion_Promedio_TMDb'].notna() & (df['Calificacion_Promedio_TMDb'] > 0)]
    
    # Calcular estadísticas de calidad
    calificacion_promedio = df_con_calificacion['Calificacion_Promedio_TMDb'].mean()
    mediana_calificacion = df_con_calificacion['Calificacion_Promedio_TMDb'].median()
    calificacion_mas_alta = df_con_calificacion['Calificacion_Promedio_TMDb'].max()
    calificacion_mas_baja = df_con_calificacion['Calificacion_Promedio_TMDb'].min()
    
    # Calcular proporción de contenido por categoría de calidad
    categorias_conteo = df_con_calificacion['Categoria_Calidad'].value_counts().reset_index()
    categorias_conteo.columns = ['Categoría', 'Conteo']
    
    # Orden personalizado para las categorías
    orden_categorias = ['Excelente', 'Bueno', 'Regular', 'Malo']
    categorias_conteo['Categoría'] = pd.Categorical(
        categorias_conteo['Categoría'], 
        categories=orden_categorias, 
        ordered=True
    )
    categorias_conteo = categorias_conteo.sort_values('Categoría')
    
    # 1. Gráfico de distribución de calificaciones
    fig_distribucion = px.histogram(
        df_con_calificacion, 
        x='Calificacion_Promedio_TMDb',
        nbins=20,
        title='Distribución de Calificaciones',
        color_discrete_sequence=['#3366CC'],
        labels={'Calificacion_Promedio_TMDb': 'Calificación', 'count': 'Frecuencia'},
        marginal='box',
        template="plotly_white"
    )
    
    fig_distribucion.update_layout(
        xaxis_title="Calificación (0-10)",
        yaxis_title="Frecuencia",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 2. Gráfico de barras para las categorías de calidad
    fig_categorias = px.bar(
        categorias_conteo,
        x='Categoría',
        y='Conteo',
        title='Contenido por Categoría de Calidad',
        text='Conteo',
        color='Categoría',
        color_discrete_map={
            'Excelente': '#28a745',
            'Bueno': '#17a2b8',
            'Regular': '#ffc107',
            'Malo': '#dc3545'
        },
        template="plotly_white"
    )
    
    fig_categorias.update_traces(
        texttemplate='%{text}',
        textposition='outside'
    )
    
    fig_categorias.update_layout(
        xaxis_title="Categoría de Calidad",
        yaxis_title="Cantidad de Visualizaciones",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 3. Comparación de calificaciones promedio: Series vs Películas
    calidad_por_tipo = df_con_calificacion.groupby('Tipo_Medio_TMDb')['Calificacion_Promedio_TMDb'].agg(
        ['mean', 'median', 'min', 'max', 'count']
    ).reset_index()
    
    calidad_por_tipo['Tipo_Medio_TMDb'] = calidad_por_tipo['Tipo_Medio_TMDb'].map({
        'tv': 'Series', 'movie': 'Películas'
    })
    
    # Preparar datos para radar chart
    radar_data = pd.DataFrame({
        'Métrica': ['Promedio', 'Mediana', 'Máxima'],
        'Series': [
            calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Series']['mean'].values[0] if not calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Series'].empty else 0,
            calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Series']['median'].values[0] if not calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Series'].empty else 0,
            calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Series']['max'].values[0] if not calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Series'].empty else 0
        ],
        'Películas': [
            calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Películas']['mean'].values[0] if not calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Películas'].empty else 0,
            calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Películas']['median'].values[0] if not calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Películas'].empty else 0,
            calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Películas']['max'].values[0] if not calidad_por_tipo[calidad_por_tipo['Tipo_Medio_TMDb'] == 'Películas'].empty else 0
        ]
    })
    
    fig_comparacion = crear_grafico_radar(
        radar_data,
        ['Series', 'Películas'],
        'Métrica',
        'Comparación de Calificaciones: Series vs Películas'
    )
    
    # 4. Top 10 contenido con mejor calificación
    top_calificacion = df_con_calificacion.sort_values('Calificacion_Promedio_TMDb', ascending=False).head(10)
    top_calificacion['Tipo'] = top_calificacion['Tipo_Medio_TMDb'].map({'tv': 'Serie', 'movie': 'Película'})
    top_calificacion['Título_Completo'] = top_calificacion['Tipo'] + ': ' + top_calificacion['Titulo_TMDb'].astype(str)
    
    fig_top = px.bar(
        top_calificacion,
        x='Calificacion_Promedio_TMDb',
        y='Título_Completo',
        title='Top 10 Contenido Mejor Calificado',
        orientation='h',
        text='Calificacion_Promedio_TMDb',
        color='Tipo',
        color_discrete_map={'Serie': '#3366CC', 'Película': '#FF9900'},
        template="plotly_white"
    )
    
    fig_top.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside'
    )
    
    fig_top.update_layout(
        xaxis_title="Calificación (0-10)",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 5. Análisis de popularidad vs calificación
    fig_popularidad = px.scatter(
        df_con_calificacion,
        x='Popularidad_TMDb',
        y='Calificacion_Promedio_TMDb',
        color='Tipo_Medio_TMDb',
        color_discrete_map={'tv': '#3366CC', 'movie': '#FF9900'},
        size='Cantidad_Votos_TMDb',
        hover_name='Titulo_TMDb',
        title='Relación entre Popularidad y Calificación',
        labels={
            'Popularidad_TMDb': 'Popularidad',
            'Calificacion_Promedio_TMDb': 'Calificación',
            'Tipo_Medio_TMDb': 'Tipo'
        },
        opacity=0.7,
        log_x=True,  # Escala logarítmica para popularidad
        size_max=30,
        template="plotly_white"
    )
    
    fig_popularidad.update_layout(
        xaxis_title="Popularidad (escala log)",
        yaxis_title="Calificación (0-10)",
        legend_title="Tipo de Contenido",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 6. Calificación promedio por género
    # Explotar la lista de géneros para analizar por género
    generos_explotados = df_con_calificacion.explode('Lista_Generos')
    generos_explotados = generos_explotados[generos_explotados['Lista_Generos'] != '']
    
    calificacion_por_genero = generos_explotados.groupby('Lista_Generos')['Calificacion_Promedio_TMDb'].agg(
        ['mean', 'count']
    ).reset_index()
    
    # Filtrar géneros con al menos 5 títulos
    calificacion_por_genero = calificacion_por_genero[calificacion_por_genero['count'] >= 5]
    calificacion_por_genero = calificacion_por_genero.sort_values('mean', ascending=False)
    
    fig_genero = px.bar(
        calificacion_por_genero.head(15),
        x='Lista_Generos',
        y='mean',
        title='Calificación Promedio por Género (Top 15)',
        text='mean',
        color='mean',
        color_continuous_scale='Viridis',
        labels={'mean': 'Calificación Promedio', 'Lista_Generos': 'Género', 'count': 'Cantidad de Títulos'},
        template="plotly_white"
    )
    
    fig_genero.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside'
    )
    
    fig_genero.update_layout(
        xaxis_title="Género",
        yaxis_title="Calificación Promedio",
        xaxis_tickangle=-45,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 7. Evolución de calificaciones a lo largo del tiempo (por año de estreno)
    # Agrupar por año de estreno
    df_con_calificacion['Anio_Estreno'] = df_con_calificacion['Fecha_Estreno_TMDb'].dt.year
    
    # Filtrar años válidos
    df_anios_validos = df_con_calificacion[df_con_calificacion['Anio_Estreno'] > 1900]
    
    # Agrupar por año y tipo
    calificacion_por_anio = df_anios_validos.groupby(['Anio_Estreno', 'Tipo_Medio_TMDb'])['Calificacion_Promedio_TMDb'].mean().reset_index()
    
    calificacion_por_anio['Tipo_Medio_TMDb'] = calificacion_por_anio['Tipo_Medio_TMDb'].map({
        'tv': 'Series', 'movie': 'Películas'
    })
    
    fig_evolucion = px.line(
        calificacion_por_anio,
        x='Anio_Estreno',
        y='Calificacion_Promedio_TMDb',
        color='Tipo_Medio_TMDb',
        title='Evolución de Calificaciones por Año de Estreno',
        labels={
            'Anio_Estreno': 'Año de Estreno',
            'Calificacion_Promedio_TMDb': 'Calificación Promedio',
            'Tipo_Medio_TMDb': 'Tipo'
        },
        markers=True,
        line_shape='spline',
        color_discrete_map={'Series': '#3366CC', 'Películas': '#FF9900'},
        template="plotly_white"
    )
    
    fig_evolucion.update_layout(
        xaxis_title="Año de Estreno",
        yaxis_title="Calificación Promedio",
        legend_title="Tipo de Contenido",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Crear layout con todos los elementos
    layout = html.Div([
        # Título y descripción
        html.Div([
            html.H1([
                html.I(className="fas fa-star me-2"),
                "Análisis de Calidad del Contenido"
            ], className="display-4 text-primary text-center mb-3"),
            html.P(
                "Exploración detallada de la calidad del contenido consumido en Netflix, basado en calificaciones de TMDb.",
                className="lead text-center mb-4"
            ),
            html.Hr(),
        ], className="my-4"),
        
        # Filtros interactivos
        html.Div([
            dbc.Card([
                dbc.CardHeader("Filtros de Análisis", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Tipo de Contenido"),
                            dcc.Dropdown(
                                id='filtro-tipo-calidad',
                                options=[
                                    {'label': 'Todos', 'value': 'todos'},
                                    {'label': 'Series', 'value': 'tv'},
                                    {'label': 'Películas', 'value': 'movie'}
                                ],
                                value='todos',
                                clearable=False
                            )
                        ], width=12, md=4),
                        
                        dbc.Col([
                            html.Label("Rango de Calificación"),
                            dcc.RangeSlider(
                                id='filtro-calificacion',
                                min=0,
                                max=10,
                                step=0.5,
                                marks={i: str(i) for i in range(0, 11, 1)},
                                value=[0, 10]
                            )
                        ], width=12, md=8),
                    ]),
                    
                    html.Div(id='contenedor-filtros-aplicados', className="mt-3")
                ])
            ], className="mb-4")
        ]),
        
        # Resumen de calidad
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H3("Resumen de Calidad", className="card-title"),
                    html.Div([
                        html.Div([
                            html.H4(f"{calificacion_promedio:.1f}", className="text-primary"),
                            html.P("Calificación Promedio", className="text-muted")
                        ], className="text-center"),
                        
                        html.Div([
                            html.H4(f"{mediana_calificacion:.1f}", className="text-primary"),
                            html.P("Mediana de Calificación", className="text-muted")
                        ], className="text-center"),
                        
                        html.Div([
                            html.H4(f"{calificacion_mas_alta:.1f}", className="text-primary"),
                            html.P("Calificación Más Alta", className="text-muted")
                        ], className="text-center"),
                        
                        html.Div([
                            html.H4(f"{calificacion_mas_baja:.1f}", className="text-primary"),
                            html.P("Calificación Más Baja", className="text-muted")
                        ], className="text-center")
                    ], className="d-flex justify-content-around")
                ], body=True, className="mb-4")
            ], width=12),
        ]),
        
        # Primera fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribución de Calificaciones", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-distribucion-calificaciones',
                            figure=fig_distribucion,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Contenido por Categoría de Calidad", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-categorias-calidad',
                            figure=fig_categorias,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
        ]),
        
        # Segunda fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Comparación Series vs Películas", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-comparacion-series-peliculas',
                            figure=fig_comparacion,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top 10 Contenido Mejor Calificado", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-top-calificacion',
                            figure=fig_top,
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
                    dbc.CardHeader("Relación Popularidad vs Calificación", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-popularidad-calificacion',
                            figure=fig_popularidad,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        # Cuarta fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Calificación Promedio por Género", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-calificacion-genero',
                            figure=fig_genero,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Evolución de Calificaciones por Año", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-evolucion-calificaciones',
                            figure=fig_evolucion,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
        ]),
        
        # Nota informativa
        dbc.Alert([
            html.H4("Interpretación de Calidad", className="alert-heading"),
            html.P([
                "Las categorías de calidad están definidas según las calificaciones de TMDb:",
                html.Ul([
                    html.Li("Excelente: Calificación ≥ 8.0"),
                    html.Li("Bueno: Calificación entre 7.0 y 7.9"),
                    html.Li("Regular: Calificación entre 6.0 y 6.9"),
                    html.Li("Malo: Calificación < 6.0")
                ])
            ]),
            html.Hr(),
            html.P(
                "Los gráficos son interactivos. Puede hacer clic en leyendas o elementos para filtrar datos y ver información detallada.",
                className="mb-0"
            )
        ], color="info", className="mt-3")
    ])
    
    return layout
