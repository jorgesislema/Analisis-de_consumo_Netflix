import pandas as pd
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from utils.data_utils import cargar_datos, crear_grafico_barras, crear_nube_palabras, crear_grafico_sunburst, crear_grafico_radar

def crear_layout_generos():
    """
    Crea el layout para la página de análisis de géneros.
    
    Returns:
        Layout de Dash con los componentes de la página de análisis de géneros
    """
    # Cargar datos
    df = cargar_datos()
    
    # Verificar si se cargaron correctamente los datos
    if df.empty:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-danger text-center"),
            html.P("No se pudieron cargar los datos para el análisis de géneros.", className="text-center")
        ])
    
    # Procesar géneros para análisis
    # Explotar la lista de géneros para tener un género por fila
    df_generos = df.explode('Lista_Generos')
    df_generos = df_generos[df_generos['Lista_Generos'].notna() & (df_generos['Lista_Generos'] != '')]
    
    # 1. Distribución general de géneros
    generos_conteo = df_generos['Lista_Generos'].value_counts().reset_index()
    generos_conteo.columns = ['Género', 'Visualizaciones']
    
    # Tomar los top 15 géneros
    top_generos = generos_conteo.head(15)
    
    fig_generos = crear_grafico_barras(
        top_generos,
        'Visualizaciones',
        'Género',
        'Top 15 Géneros Más Vistos',
        orientacion='h',
        color_col='Visualizaciones'
    )
    
    # 2. Géneros por tipo de contenido (Series vs Películas)
    generos_por_tipo = df_generos.groupby(['Lista_Generos', 'Tipo_Medio_TMDb']).size().reset_index(name='Conteo')
    generos_por_tipo['Tipo'] = generos_por_tipo['Tipo_Medio_TMDb'].map({'tv': 'Series', 'movie': 'Películas'})
    
    # Filtrar solo los géneros principales para evitar sobrecarga visual
    generos_principales = generos_conteo.head(10)['Género'].tolist()
    generos_por_tipo_filtrado = generos_por_tipo[generos_por_tipo['Lista_Generos'].isin(generos_principales)]
    
    fig_generos_tipo = px.bar(
        generos_por_tipo_filtrado,
        x='Lista_Generos',
        y='Conteo',
        color='Tipo',
        title='Géneros por Tipo de Contenido',
        barmode='group',
        color_discrete_map={'Series': '#3366CC', 'Películas': '#FF9900'},
        template="plotly_white"
    )
    
    fig_generos_tipo.update_layout(
        xaxis_title="Género",
        yaxis_title="Número de Visualizaciones",
        xaxis_tickangle=-45,
        legend_title="Tipo de Contenido",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 3. Evolución temporal de géneros
    # Agrupar por año y género
    generos_por_anio = df_generos.groupby(['Anio', 'Lista_Generos']).size().reset_index(name='Visualizaciones')
    
    # Filtrar años con datos suficientes y géneros principales
    anios_validos = df['Anio'].value_counts()[df['Anio'].value_counts() > 30].index.tolist()
    generos_por_anio_filtrado = generos_por_anio[
        (generos_por_anio['Anio'].isin(anios_validos)) & 
        (generos_por_anio['Lista_Generos'].isin(generos_principales[:5]))
    ]
    
    fig_generos_tiempo = px.line(
        generos_por_anio_filtrado,
        x='Anio',
        y='Visualizaciones',
        color='Lista_Generos',
        title='Evolución de Géneros a lo Largo del Tiempo',
        markers=True,
        template="plotly_white"
    )
    
    fig_generos_tiempo.update_layout(
        xaxis_title="Año",
        yaxis_title="Número de Visualizaciones",
        legend_title="Género",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # 4. Combinaciones de géneros más frecuentes
    # Crear un diccionario para almacenar pares de géneros
    generos_combinados = {}
    
    for i, row in df.iterrows():
        generos = row['Lista_Generos']
        if isinstance(generos, list) and len(generos) > 1:
            # Considerar todas las combinaciones posibles de pares
            for i in range(len(generos)):
                for j in range(i+1, len(generos)):
                    if generos[i] != '' and generos[j] != '':
                        # Ordenar para evitar duplicados (A,B) vs (B,A)
                        par = tuple(sorted([generos[i], generos[j]]))
                        generos_combinados[par] = generos_combinados.get(par, 0) + 1
    
    # Convertir a DataFrame y ordenar
    combinaciones_df = pd.DataFrame([
        {'Género 1': g1, 'Género 2': g2, 'Frecuencia': freq}
        for (g1, g2), freq in generos_combinados.items()
    ])
    
    if not combinaciones_df.empty:
        combinaciones_df = combinaciones_df.sort_values('Frecuencia', ascending=False).head(15)
        
        fig_combinaciones = px.bar(
            combinaciones_df,
            x='Frecuencia',
            y=combinaciones_df.apply(lambda x: f"{x['Género 1']} + {x['Género 2']}", axis=1),
            title='Top 15 Combinaciones de Géneros',
            orientation='h',
            color='Frecuencia',
            color_continuous_scale='Viridis',
            template="plotly_white"
        )
        
        fig_combinaciones.update_layout(
            xaxis_title="Frecuencia",
            yaxis_title="Combinación de Géneros",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=50, b=10)
        )
    else:
        # Crear un gráfico vacío si no hay combinaciones
        fig_combinaciones = go.Figure()
        fig_combinaciones.update_layout(
            title="No se encontraron combinaciones de géneros suficientes",
            template="plotly_white"
        )
    
    # 5. Gráfico de géneros por día de la semana (radar chart o "caracol")
    generos_dia_semana = df_generos.groupby(['Dia_Semana', 'Lista_Generos']).size().reset_index(name='Conteo')
    
    # Filtrar solo los géneros principales
    generos_dia_semana_filtrado = generos_dia_semana[generos_dia_semana['Lista_Generos'].isin(generos_principales[:5])]
    
    # Pivotar los datos para el gráfico de radar
    radar_data = pd.pivot_table(
        generos_dia_semana_filtrado,
        values='Conteo',
        index='Dia_Semana',
        columns='Lista_Generos',
        fill_value=0
    ).reset_index()
    
    # Ordenar días de la semana
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    radar_data['Dia_Semana'] = pd.Categorical(radar_data['Dia_Semana'], categories=dias_orden, ordered=True)
    radar_data = radar_data.sort_values('Dia_Semana')
    
    fig_radar = crear_grafico_radar(
        radar_data,
        generos_principales[:5],
        'Dia_Semana',
        'Géneros por Día de la Semana'
    )
    
    # 6. Gráfico Sunburst para jerarquía de visualización (alternativa al pie chart)
    # Agrupar por tipo de contenido y género
    jerarquia_df = df_generos.groupby(['Tipo_Medio_TMDb', 'Lista_Generos']).size().reset_index(name='Visualizaciones')
    jerarquia_df['Tipo'] = jerarquia_df['Tipo_Medio_TMDb'].map({'tv': 'Series', 'movie': 'Películas'})
    
    fig_sunburst = crear_grafico_sunburst(
        jerarquia_df,
        ['Tipo', 'Lista_Generos'],
        'Visualizaciones',
        'Jerarquía de Visualizaciones por Tipo y Género'
    )
    
    # 7. Nube de palabras de géneros
    generos_dict = generos_conteo.set_index('Género')['Visualizaciones'].to_dict()
    
    fig_nube = crear_nube_palabras(
        df_generos,
        'Lista_Generos',
        generos_dict,
        'Nube de Géneros'
    )
    
    # Crear layout con todos los elementos
    layout = html.Div([
        # Título y descripción
        html.Div([
            html.H1([
                html.I(className="fas fa-film me-2"),
                "Análisis de Géneros"
            ], className="display-4 text-primary text-center mb-3"),
            html.P(
                "Exploración detallada de los géneros de contenido consumidos en Netflix.",
                className="lead text-center mb-4"
            ),
            html.Hr(),
        ], className="my-4"),
        
        # Filtros interactivos
        html.Div([
            dbc.Card([
                dbc.CardHeader("Filtros de Análisis de Géneros", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Tipo de Contenido"),
                            dcc.Dropdown(
                                id='filtro-tipo-generos',
                                options=[
                                    {'label': 'Todos', 'value': 'todos'},
                                    {'label': 'Series', 'value': 'tv'},
                                    {'label': 'Películas', 'value': 'movie'}
                                ],
                                value='todos',
                                clearable=False
                            )
                        ], width=12, md=6),
                        
                        dbc.Col([
                            html.Label("Período de Tiempo"),
                            dcc.Dropdown(
                                id='filtro-periodo-generos',
                                options=[
                                    {'label': 'Todo el período', 'value': 'todo'},
                                    {'label': 'Último año', 'value': 'ultimo_anio'},
                                    {'label': 'Últimos 3 meses', 'value': 'ultimos_3_meses'}
                                ],
                                value='todo',
                                clearable=False
                            )
                        ], width=12, md=6),
                    ]),
                    
                    html.Div(id='contenedor-filtros-generos-aplicados', className="mt-3")
                ])
            ], className="mb-4")
        ]),
        
        # Primera fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Géneros Más Vistos", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-top-generos',
                            figure=fig_generos,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Nube de Géneros", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-nube-generos',
                            figure=fig_nube,
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
                    dbc.CardHeader("Géneros por Tipo de Contenido", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-generos-tipo',
                            figure=fig_generos_tipo,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        # Tercera fila de gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Evolución de Géneros a lo Largo del Tiempo", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-generos-tiempo',
                            figure=fig_generos_tiempo,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Combinaciones de Géneros", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-combinaciones-generos',
                            figure=fig_combinaciones,
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
                    dbc.CardHeader("Géneros por Día de la Semana", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-generos-dia',
                            figure=fig_radar,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Jerarquía de Visualizaciones", className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='grafico-jerarquia-generos',
                            figure=fig_sunburst,
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], width=12, md=6),
        ]),
        
        # Nota informativa
        dbc.Alert([
            html.H4("Interpretación del Análisis de Géneros", className="alert-heading"),
            html.P([
                "El análisis de géneros proporciona insights sobre sus preferencias de contenido:",
                html.Ul([
                    html.Li("Identifique sus géneros favoritos y cómo varían entre series y películas"),
                    html.Li("Descubra patrones temporales en sus preferencias de género"),
                    html.Li("Explore las combinaciones de géneros más frecuentes en su historial")
                ])
            ]),
            html.Hr(),
            html.P(
                "El gráfico de radar (o 'caracol') muestra la distribución de géneros por día de la semana, permitiendo identificar patrones específicos.",
                className="mb-0"
            )
        ], color="info", className="mt-3")
    ])
    
    return layout
