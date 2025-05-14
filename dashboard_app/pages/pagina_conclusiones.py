import pandas as pd
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from utils.data_utils import cargar_datos, crear_grafico_barras, crear_grafico_linea

def crear_layout_conclusiones():
    """
    Crea el layout para la página de conclusiones y recomendaciones.
    
    Returns:
        Layout de Dash con los componentes de la página de conclusiones
    """
    # Cargar datos
    df = cargar_datos()
    
    # Verificar si se cargaron correctamente los datos
    if df.empty:
        return html.Div([
            html.H1("Error al cargar los datos", className="text-danger text-center"),
            html.P("No se pudieron cargar los datos para las conclusiones.", className="text-center")
        ])
    
    # Extraer insights clave
    # 1. Días de mayor consumo
    vis_dia_semana = df['Dia_Semana'].value_counts().reset_index()
    vis_dia_semana.columns = ['Día', 'Visualizaciones']
    
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    vis_dia_semana['Día'] = pd.Categorical(vis_dia_semana['Día'], categories=dias_orden, ordered=True)
    vis_dia_semana = vis_dia_semana.sort_values('Día')
    
    dia_mas_popular = vis_dia_semana.loc[vis_dia_semana['Visualizaciones'].idxmax()]['Día']
    
    # 2. Horas pico
    vis_hora = df['Hora'].value_counts().reset_index()
    vis_hora.columns = ['Hora', 'Visualizaciones']
    hora_pico = vis_hora.sort_values('Visualizaciones', ascending=False).iloc[0]['Hora']
    
    # 3. Género favorito
    df_generos = df.explode('Lista_Generos')
    df_generos = df_generos[df_generos['Lista_Generos'].notna() & (df_generos['Lista_Generos'] != '')]
    genero_favorito = df_generos['Lista_Generos'].value_counts().index[0]
    
    # 4. Calidad promedio
    df_con_calificacion = df[df['Calificacion_Promedio_TMDb'].notna() & (df['Calificacion_Promedio_TMDb'] > 0)]
    calidad_promedio = df_con_calificacion['Calificacion_Promedio_TMDb'].mean()
    
    # 5. Título más visto
    titulo_mas_visto = df['Titulo_TMDb'].value_counts().index[0]
    
    # 6. Proporción series vs películas
    total_series = df[df['Es_Serie']].shape[0]
    total_peliculas = df[df['Es_Pelicula']].shape[0]
    
    proporcion = "Series" if total_series > total_peliculas else "Películas"
    
    # Gráfico resumen de preferencias
    # Crear un DataFrame para las métricas clave
    metricas_resumen = pd.DataFrame({
        'Categoría': ['Series', 'Películas', 'Contenido ≥ 8.0', 'Contenido < 8.0', 'Fin de semana', 'Entre semana'],
        'Valor': [
            total_series,
            total_peliculas,
            df_con_calificacion[df_con_calificacion['Calificacion_Promedio_TMDb'] >= 8.0].shape[0],
            df_con_calificacion[df_con_calificacion['Calificacion_Promedio_TMDb'] < 8.0].shape[0],
            df[df['Dia_Semana'].isin(['Sábado', 'Domingo'])].shape[0],
            df[~df['Dia_Semana'].isin(['Sábado', 'Domingo'])].shape[0]
        ]
    })
    
    fig_resumen = px.bar(
        metricas_resumen,
        x='Categoría',
        y='Valor',
        title='Resumen de Preferencias',
        color='Categoría',
        template="plotly_white",
        text='Valor'
    )
    
    fig_resumen.update_traces(
        texttemplate='%{text}',
        textposition='outside'
    )
    
    fig_resumen.update_layout(
        xaxis_title="",
        yaxis_title="Número de Visualizaciones",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Crear layout con todos los elementos
    layout = html.Div([
        # Título y descripción
        html.Div([
            html.H1([
                html.I(className="fas fa-lightbulb me-2"),
                "Conclusiones y Recomendaciones"
            ], className="display-4 text-primary text-center mb-3"),
            html.P(
                "Resumen de insights clave y recomendaciones personalizadas basadas en tu historial de visualización.",
                className="lead text-center mb-4"
            ),
            html.Hr(),
        ], className="my-4"),
        
        # Resumen de insights
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3("Insights Clave", className="text-center m-0"),
                        className="bg-primary text-white"
                    ),
                    dbc.CardBody([
                        dbc.Row([
                            # Principales hallazgos
                            dbc.Col([
                                html.Div([
                                    html.H4("Patrones de Consumo", className="border-bottom pb-2"),
                                    html.Ul([
                                        html.Li([
                                            html.Strong("Día favorito: "),
                                            f"{dia_mas_popular}"
                                        ]),
                                        html.Li([
                                            html.Strong("Hora pico: "),
                                            f"{hora_pico}:00"
                                        ]),
                                        html.Li([
                                            html.Strong("Preferencia de contenido: "),
                                            f"{proporcion}"
                                        ]),
                                    ], className="mb-4")
                                ]),
                                html.Div([
                                    html.H4("Preferencias de Contenido", className="border-bottom pb-2"),
                                    html.Ul([
                                        html.Li([
                                            html.Strong("Género favorito: "),
                                            f"{genero_favorito}"
                                        ]),
                                        html.Li([
                                            html.Strong("Calidad promedio: "),
                                            f"{calidad_promedio:.1f}/10"
                                        ]),
                                        html.Li([
                                            html.Strong("Título más visto: "),
                                            f"{titulo_mas_visto}"
                                        ]),
                                    ], className="mb-4")
                                ]),
                            ], width=12, md=6),
                            
                            # Gráfico resumen
                            dbc.Col([
                                dcc.Graph(
                                    figure=fig_resumen,
                                    config={'displayModeBar': False}
                                )
                            ], width=12, md=6),
                        ]),
                    ])
                ], className="mb-4")
            ], width=12),
        ]),
        
        # Conclusiones principales
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3("Conclusiones Principales", className="text-center m-0"),
                        className="bg-primary text-white"
                    ),
                    dbc.CardBody([
                        html.Ol([
                            html.Li([
                                html.Strong("Patrones Temporales:"),
                                html.P([
                                    f"Tu consumo de Netflix se concentra principalmente los {dia_mas_popular} alrededor de las {hora_pico}:00 horas. ",
                                    "Este patrón sugiere que prefieres ver contenido durante momentos específicos de la semana, ",
                                    "lo que podría estar relacionado con tu rutina diaria."
                                ])
                            ], className="mb-3"),
                            
                            html.Li([
                                html.Strong("Calidad del Contenido:"),
                                html.P([
                                    f"El contenido que consumes tiene una calificación promedio de {calidad_promedio:.1f}/10, ",
                                    "lo que indica una preferencia por contenido de " + 
                                    ("alta" if calidad_promedio >= 7.5 else "media" if calidad_promedio >= 6.5 else "baja") + 
                                    " calidad según las calificaciones de TMDb."
                                ])
                            ], className="mb-3"),
                            
                            html.Li([
                                html.Strong("Preferencias de Género:"),
                                html.P([
                                    f"Tu género favorito es {genero_favorito}, lo que se refleja en la mayoría de tus visualizaciones. ",
                                    "Este patrón constante sugiere una clara preferencia temática en tu selección de contenido."
                                ])
                            ], className="mb-3"),
                            
                            html.Li([
                                html.Strong("Balance de Tipo de Contenido:"),
                                html.P([
                                    f"Muestras una mayor inclinación hacia {'series' if total_series > total_peliculas else 'películas'}, ",
                                    f"con una proporción aproximada de {total_series/(total_series+total_peliculas)*100:.1f}% series vs ",
                                    f"{total_peliculas/(total_series+total_peliculas)*100:.1f}% películas. ",
                                    "Esto sugiere una preferencia por " + 
                                    ("narrativas más largas y desarrollo de personajes." if total_series > total_peliculas else "historias autoconclusivas.")
                                ])
                            ], className="mb-3"),
                            
                            html.Li([
                                html.Strong("Consistencia de Visualización:"),
                                html.P([
                                    "Tu patrón de visualización muestra " + 
                                    ("picos y valles significativos" if df.groupby(['Anio', 'Mes_Num']).size().std() > df.groupby(['Anio', 'Mes_Num']).size().mean()/2 
                                    else "bastante consistencia") +
                                    " a lo largo del tiempo, lo que indica " +
                                    ("un consumo variable que podría estar influenciado por factores externos o disponibilidad de nuevo contenido." 
                                    if df.groupby(['Anio', 'Mes_Num']).size().std() > df.groupby(['Anio', 'Mes_Num']).size().mean()/2 
                                    else "hábitos de visualización estables y bien establecidos.")
                                ])
                            ], className="mb-3"),
                        ])
                    ])
                ], className="mb-4")
            ], width=12),
        ]),
        
        # Recomendaciones personalizadas
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3("Recomendaciones Personalizadas", className="text-center m-0"),
                        className="bg-primary text-white"
                    ),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H4([
                                        html.I(className="fas fa-check-circle text-success me-2"),
                                        "Optimiza tu Experiencia"
                                    ]),
                                    html.Ul([
                                        html.Li([
                                            html.Strong("Programa tu Tiempo de Visualización:"),
                                            html.P([
                                                f"Aprovecha al máximo tus {dia_mas_popular} creando una lista de reproducción para ese día."
                                            ])
                                        ]),
                                        html.Li([
                                            html.Strong("Explora Contenido Similar:"),
                                            html.P([
                                                f"Basado en tu preferencia por {genero_favorito}, busca nuevo contenido en ese género, ",
                                                f"especialmente en {'series' if total_series > total_peliculas else 'películas'}."
                                            ])
                                        ]),
                                        html.Li([
                                            html.Strong("Diversifica tus Opciones:"),
                                            html.P([
                                                "Considera explorar géneros relacionados o complementarios a tus favoritos para descubrir nuevo contenido."
                                            ])
                                        ]),
                                    ])
                                ])
                            ], width=12, md=6),
                            
                            dbc.Col([
                                html.Div([
                                    html.H4([
                                        html.I(className="fas fa-lightbulb text-warning me-2"),
                                        "Mejora tu Selección"
                                    ]),
                                    html.Ul([
                                        html.Li([
                                            html.Strong("Considera la Calidad:"),
                                            html.P([
                                                "Utiliza filtros de calificación en Netflix para encontrar contenido mejor valorado ",
                                                f"(busca títulos con calificación superior a {max(calidad_promedio, 7.5):.1f})."
                                            ])
                                        ]),
                                        html.Li([
                                            html.Strong("Equilibra tu Consumo:"),
                                            html.P([
                                                "Prueba alternar entre series y películas para una experiencia más variada y adaptable a tu tiempo disponible."
                                            ])
                                        ]),
                                        html.Li([
                                            html.Strong("Utiliza las Listas:"),
                                            html.P([
                                                "Crea listas temáticas basadas en tus géneros favoritos para facilitar la selección de contenido."
                                            ])
                                        ]),
                                    ])
                                ])
                            ], width=12, md=6),
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H4("Recomendaciones de Contenido", className="text-center mt-4 mb-3"),
                                    html.P([
                                        "Basado en tus preferencias, podrías disfrutar de contenido que combine ",
                                        f"{genero_favorito} con alta calificación, especialmente en formato de {'series' if total_series > total_peliculas else 'películas'}."
                                    ], className="text-center"),
                                    html.Div([
                                        dbc.Button(
                                            [html.I(className="fas fa-sync-alt me-2"), "Generar Recomendaciones Personalizadas"],
                                            color="primary",
                                            className="mx-auto d-block mt-3",
                                            id="btn-recomendaciones"
                                        ),
                                        html.Div(id="contenedor-recomendaciones", className="mt-3")
                                    ])
                                ])
                            ], width=12),
                        ]),
                    ])
                ], className="mb-4")
            ], width=12),
        ]),
        
        # Conclusión final
        dbc.Alert([
            html.H4("Resumen Final", className="alert-heading"),
            html.P([
                "Este análisis de tu consumo de Netflix revela patrones significativos en tus hábitos de visualización, ",
                "desde tus preferencias de género hasta tus horarios favoritos. Utilizando esta información, ",
                "puedes tomar decisiones más informadas sobre qué y cuándo ver contenido, optimizando así tu experiencia en la plataforma."
            ]),
            html.Hr(),
            html.P([
                "Este dashboard ha sido diseñado para proporcionar una visión completa y detallada de tus patrones de consumo. ",
                "Explora las diferentes secciones para obtener insights más específicos y personalizar tu experiencia de streaming."
            ], className="mb-0")
        ], color="success", className="mt-3")
    ])
    
    return layout
