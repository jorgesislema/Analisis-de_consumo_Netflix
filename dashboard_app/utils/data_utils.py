import pandas as pd
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def cargar_datos():
    """
    Carga y preprocesa los datos de Netflix para el dashboard.
    
    Returns:
        DataFrame: DataFrame con los datos procesados
    """
    # Ruta del archivo
    data_path = os.path.join('data', 'processed', 'netflix_eda_processed.csv')
    
    try:
        # Cargar el dataset
        df = pd.read_csv(data_path, low_memory=False)
        
        # Convertir fechas a formato datetime
        df['Fecha_Visualizacion'] = pd.to_datetime(df['Fecha_Visualizacion'], errors='coerce')
        df['Fecha_Estreno_TMDb'] = pd.to_datetime(df['Fecha_Estreno_TMDb'], errors='coerce')
        
        # Eliminar filas con fecha de visualización faltante
        df.dropna(subset=['Fecha_Visualizacion'], inplace=True)
        
        # Crear columnas basadas en fecha para análisis temporal
        df['Anio'] = df['Fecha_Visualizacion'].dt.year
        df['Mes_Num'] = df['Fecha_Visualizacion'].dt.month
        df['Dia_Mes'] = df['Fecha_Visualizacion'].dt.day
        df['Dia_Semana_Num'] = df['Fecha_Visualizacion'].dt.dayofweek  # 0=Lunes, 6=Domingo
        df['Hora'] = df['Fecha_Visualizacion'].dt.hour
        df['Semana_Anio'] = df['Fecha_Visualizacion'].dt.isocalendar().week
        
        # Nombres en español para meses y días
        meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        
        df['Mes'] = df['Mes_Num'].map(meses_es)
        df['Dia_Semana'] = df['Dia_Semana_Num'].map(dias_es)
        
        # Procesamiento de géneros para análisis
        if 'Generos_TMDb' in df.columns:
            # Rellenar valores nulos con cadena vacía
            df['Generos_TMDb'] = df['Generos_TMDb'].fillna('')
            
            # Crear lista de géneros para cada título
            df['Lista_Generos'] = df['Generos_TMDb'].apply(
                lambda x: [genre.strip() for genre in x.split(',')] if x else []
            )
        
        # Indicadores para análisis de tipo de contenido
        df['Es_Serie'] = df['Tipo_Medio_TMDb'] == 'tv'
        df['Es_Pelicula'] = df['Tipo_Medio_TMDb'] == 'movie'
        
        # Calcular tiempo desde el estreno hasta la visualización (en días)
        df['Tiempo_Desde_Estreno'] = (df['Fecha_Visualizacion'] - df['Fecha_Estreno_TMDb']).dt.days
        
        # Convertir Mes y Dia_Semana a categorías ordenadas
        df['Mes'] = pd.Categorical(df['Mes'], categories=list(meses_es.values()), ordered=True)
        df['Dia_Semana'] = pd.Categorical(df['Dia_Semana'], categories=list(dias_es.values()), ordered=True)
        
        # Procesamiento específico para el análisis de calidad
        if 'Calificacion_Promedio_TMDb' in df.columns:
            # Convertir a valor numérico si no lo es
            df['Calificacion_Promedio_TMDb'] = pd.to_numeric(df['Calificacion_Promedio_TMDb'], errors='coerce')
            
            # Crear categorías de calidad basado en calificaciones
            condiciones = [
                (df['Calificacion_Promedio_TMDb'] >= 8.0),
                (df['Calificacion_Promedio_TMDb'] >= 7.0) & (df['Calificacion_Promedio_TMDb'] < 8.0),
                (df['Calificacion_Promedio_TMDb'] >= 6.0) & (df['Calificacion_Promedio_TMDb'] < 7.0),
                (df['Calificacion_Promedio_TMDb'] < 6.0)
            ]
            categorias = ['Excelente', 'Bueno', 'Regular', 'Malo']
            df['Categoria_Calidad'] = np.select(condiciones, categorias, default='Sin calificación')
        
        return df
    
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        # Retornar un DataFrame vacío en caso de error
        return pd.DataFrame()

def crear_mapa_calor(df, x_col, y_col, valor_col, titulo):
    """
    Crea un mapa de calor interactivo
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para el eje X
        y_col: Columna para el eje Y
        valor_col: Columna para calcular los valores (se realizará un count)
        titulo: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    # Crear tabla pivote para el mapa de calor
    heatmap_data = pd.pivot_table(
        df, 
        values=valor_col,
        index=y_col, 
        columns=x_col,
        aggfunc='count',
        fill_value=0
    )
    
    # Crear mapa de calor
    fig = px.imshow(
        heatmap_data,
        labels=dict(x=x_col, y=y_col, color="Visualizaciones"),
        title=titulo,
        color_continuous_scale='YlGnBu',
        aspect="auto"
    )
    
    # Mejorar formato
    fig.update_layout(
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def crear_grafico_barras(df, x_col, y_col, titulo, orientacion='v', color_col=None, limite=None):
    """
    Crea un gráfico de barras interactivo
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para el eje X
        y_col: Columna para el eje Y
        titulo: Título del gráfico
        orientacion: Orientación del gráfico ('v' para vertical, 'h' para horizontal)
        color_col: Columna para colorear las barras
        limite: Número máximo de barras a mostrar
    
    Returns:
        Figura de Plotly
    """
    # Limitar si es necesario
    if limite:
        df = df.head(limite)
    
    # Parámetros según la orientación
    if orientacion == 'h':
        x, y = y_col, x_col
    else:
        x, y = x_col, y_col
    
    # Crear gráfico de barras
    fig = px.bar(
        df, 
        x=x, 
        y=y,
        title=titulo,
        color=color_col if color_col else None,
        orientation=orientacion,
        text=y_col,
        template="plotly_white"
    )
    
    # Mejorar formato
    fig.update_traces(
        texttemplate='%{text:.1f}' if df[y_col].dtype == 'float' else '%{text:.0f}',
        textposition='outside',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5
    )
    
    fig.update_layout(
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def crear_grafico_barras_apiladas(df, x_col, y_col, color_col, titulo):
    """
    Crea un gráfico de barras apiladas interactivo
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para el eje X
        y_col: Columna para el eje Y
        color_col: Columna para agrupar y colorear
        titulo: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = px.bar(
        df, 
        x=x_col, 
        y=y_col,
        color=color_col,
        title=titulo,
        barmode='stack',
        template="plotly_white"
    )
    
    fig.update_layout(
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def crear_grafico_linea(df, x_col, y_col, titulo, color_col=None, tipo_linea='markers+lines'):
    """
    Crea un gráfico de línea interactivo
    
    Args:
        df: DataFrame con los datos
        x_col: Columna para el eje X
        y_col: Columna para el eje Y
        titulo: Título del gráfico
        color_col: Columna para colorear diferentes líneas
        tipo_linea: Tipo de línea ('markers+lines', 'lines', 'markers')
    
    Returns:
        Figura de Plotly
    """
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col,
        color=color_col,
        title=titulo,
        template="plotly_white",
        markers=(tipo_linea != 'lines')
    )
    
    fig.update_traces(
        line=dict(width=2),
        marker=dict(size=6)
    )
    
    fig.update_layout(
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def crear_grafico_radar(df, r_cols, theta_col, titulo):
    """
    Crea un gráfico de radar (también llamado 'caracol' en algunos contextos)
    
    Args:
        df: DataFrame con los datos
        r_cols: Lista de columnas para los valores radiales
        theta_col: Columna para las categorías angulares
        titulo: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    for col in r_cols:
        fig.add_trace(go.Scatterpolar(
            r=df[col],
            theta=df[theta_col],
            fill='toself',
            name=col
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, df[r_cols].values.max() * 1.1]
            )),
        title=titulo,
        template="plotly_white",
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def crear_nube_palabras(df, texto_col, frecuencia_dict, titulo):
    """
    Crea una nube de palabras y la convierte en una figura de Plotly
    
    Args:
        df: DataFrame con los datos
        texto_col: Columna con los textos para la nube
        frecuencia_dict: Diccionario con frecuencias
        titulo: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    # Crear nube de palabras
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=100,
        prefer_horizontal=1,
        min_font_size=10,
        max_font_size=60,
        random_state=42
    ).generate_from_frequencies(frecuencia_dict)
    
    # Crear figura de matplotlib
    fig_mpl = plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(titulo)
    plt.tight_layout()
    
    # Convertir a imagen base64 para Plotly
    import io
    import base64
    
    buf = io.BytesIO()
    fig_mpl.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close(fig_mpl)
    
    # Crear figura de Plotly para mostrar la imagen
    fig = go.Figure()
    
    fig.add_trace(
        go.Image(
            source=f'data:image/png;base64,{img_str}'
        )
    )
    
    fig.update_layout(
        title=titulo,
        width=800,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        template="plotly_white"
    )
    
    return fig

def crear_grafico_sunburst(df, path_cols, values_col, titulo):
    """
    Crea un gráfico de sunburst (alternativa al gráfico de pastel)
    
    Args:
        df: DataFrame con los datos
        path_cols: Lista de columnas para las jerarquías
        values_col: Columna para los valores
        titulo: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = px.sunburst(
        df, 
        path=path_cols, 
        values=values_col,
        title=titulo,
        template="plotly_white"
    )
    
    fig.update_layout(
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def crear_grafico_indicadores(valores, titulos, subtitulo_general):
    """
    Crea un panel de indicadores
    
    Args:
        valores: Lista de valores para los indicadores
        titulos: Lista de títulos para los indicadores
        subtitulo_general: Subtítulo general para el panel
    
    Returns:
        Figura de Plotly
    """
    # Determinar número de filas y columnas
    n = len(valores)
    cols = min(n, 3)  # Máximo 3 columnas
    rows = (n + cols - 1) // cols  # Calcular número de filas necesarias
    
    # Crear especificaciones para los subplots
    specs = [[{"type": "indicator"} for _ in range(cols)] for _ in range(rows)]
    
    # Crear figura con subplots
    fig = make_subplots(
        rows=rows, 
        cols=cols,
        specs=specs,
        subplot_titles=titulos
    )
    
    # Añadir indicadores
    for i, valor in enumerate(valores):
        row = i // cols + 1
        col = i % cols + 1
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=valor,
                number={"font": {"size": 40}},
                domain={"row": row-1, "column": col-1}
            ),
            row=row, col=col
        )
    
    # Actualizar layout
    fig.update_layout(
        title_text=subtitulo_general,
        height=150 * rows,  # Altura ajustada según número de filas
        font=dict(size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig
