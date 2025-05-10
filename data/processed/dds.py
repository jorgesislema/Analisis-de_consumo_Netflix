# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_eda_processed.csv")
    df['Fecha_Visualizacion'] = pd.to_datetime(df['Fecha_Visualizacion'], errors='coerce')
    df['Nombre_Mes'] = df['Fecha_Visualizacion'].dt.strftime('%B')
    df['Numero_Mes'] = df['Fecha_Visualizacion'].dt.month
    df['Anio'] = df['Fecha_Visualizacion'].dt.year
    df['Dia'] = df['Fecha_Visualizacion'].dt.day
    return df

df = load_data()

# Estilo oscuro tipo Blue World
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #0f1117;
        color: #ffffff;
    }
    .css-18e3th9 {
        background-color: #0f1117;
    }
    .stMetric label, .stMetric div {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("📺 Netflix Analytics")
page = st.sidebar.radio("Navegar a:", ["📊 Resumen General", "📅 Análisis Temporal", "🎭 Géneros y Tendencias"])

# ------------------------- RESUMEN GENERAL --------------------------
if page == "📊 Resumen General":
    st.markdown("""
    # 📊 Resumen General
    Este panel muestra un resumen ejecutivo del comportamiento de visualización.
    Incluye indicadores clave (KPIs) y visualizaciones generales.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Visualizaciones", int(df.shape[0]), help="Total de episodios vistos en el periodo")
    with col2:
        st.metric("Promedio Calificación", round(df['Calificacion_Promedio_TMDb'].mean(), 2), help="Promedio TMDb de las visualizaciones")
    with col3:
        st.metric("Popularidad Promedio", round(df['Popularidad_TMDb'].mean(), 2), help="Promedio de popularidad de los títulos vistos")

    st.markdown("### 📈 Visualizaciones por Mes")
    resumen = df.groupby(['Numero_Mes', 'Nombre_Mes']).agg({
        'Titulo_Original_Netflix': 'count',
        'Calificacion_Promedio_TMDb': 'mean'
    }).reset_index().rename(columns={'Titulo_Original_Netflix': 'Visualizaciones'})
    resumen = resumen.sort_values("Numero_Mes")
    fig = px.bar(resumen, x='Nombre_Mes', y='Visualizaciones', template='plotly_dark',
                 color='Visualizaciones', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧮 Distribución por Año")
    por_anio = df.groupby("Anio").size().reset_index(name="Visualizaciones")
    fig_a = px.pie(por_anio, names='Anio', values='Visualizaciones', template='plotly_dark')
    st.plotly_chart(fig_a, use_container_width=True)

    st.markdown("### 🔝 Títulos Más Vistos")
    top_titles = df['Titulo_Original_Netflix'].value_counts().reset_index()
    top_titles.columns = ['Titulo', 'Visualizaciones']
    st.dataframe(top_titles.head(10), height=250)

    st.markdown("### 🕵️‍♂️ Calificación Promedio por Año")
    calif_anual = df.groupby("Anio")["Calificacion_Promedio_TMDb"].mean().reset_index()
    fig_b = px.bar(calif_anual, x='Anio', y='Calificacion_Promedio_TMDb', template='plotly_dark',
                   title='Calificación promedio por año')
    st.plotly_chart(fig_b, use_container_width=True)

    st.markdown("### 📌 Conclusiones")
    st.markdown("""
    - El contenido con mayor visualización se concentra en 2025.
    - La calificación promedio es alta, lo cual indica buena recepción.
    - La distribución de géneros y temporalidad permite identificar patrones de consumo.
    - El año 2025 muestra también un alto promedio de calificación.
    """)
