# --- powerbi_prep.py ---
# Script para preparar los datos para Power BI a partir de los datos enriquecidos

import pandas as pd
import os
import numpy as np
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Rutas de Archivos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ENRICHED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'netflix_viewing_enriched.csv')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'netflix_eda_processed.csv')

# Archivos adicionales para análisis específicos
CALIDAD_TIPO_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'promedio_calidad_tipo.csv')
RESUMEN_CALIDAD_TIPO_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'resumen_calidad_tipo.csv')
GENEROS_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'netflix_analisis_generos.csv')
GENEROS_POPULARES_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'generos_populares.csv')

def preparar_datos_para_powerbi():
    """
    Prepara los datos enriquecidos para su uso en Power BI
    generando los archivos necesarios para los diferentes análisis
    """
    logging.info("Iniciando preparación de datos para Power BI...")
    
    # Verificar si existe el archivo de datos enriquecidos
    if not os.path.exists(ENRICHED_DATA_PATH):
        logging.error(f"No se encontró el archivo de datos enriquecidos: {ENRICHED_DATA_PATH}")
        logging.info("Intentando usar el archivo de ejemplo...")
        
        # Cargar datos de ejemplo de Netflix (si el archivo real no existe)
        raw_data_path = os.path.join(PROJECT_ROOT, 'data', 'raw', 'NetflixViewingHistory.csv')
        if not os.path.exists(raw_data_path):
            logging.error(f"No se encontró ni el archivo enriquecido ni el de historial: {raw_data_path}")
            return
        
        df = pd.read_csv(raw_data_path)
        logging.info(f"Cargado archivo de historial con {len(df)} registros")
        
        # Crear datos simulados para el análisis
        df.rename(columns={'Title': 'Titulo_Original_Netflix', 'Date': 'Fecha_Visualizacion'}, inplace=True)
        df['Fecha_Visualizacion'] = pd.to_datetime(df['Fecha_Visualizacion'], errors='coerce')
        df['Titulo_Limpio_Busqueda'] = df['Titulo_Original_Netflix'].str.split(':', n=1).str[0]
        
        # Simular datos de TMDb
        df['ID_TMDb'] = np.random.randint(1000, 10000, size=len(df))
        df['Titulo_TMDb'] = df['Titulo_Limpio_Busqueda']
        
        # Géneros aleatorios
        generos = ['Drama', 'Comedy', 'Action', 'Thriller', 'Romance', 'Sci-Fi', 'Horror', 'Documentary']
        df['Generos_TMDb'] = [', '.join(np.random.choice(generos, size=np.random.randint(1, 3))) for _ in range(len(df))]
        
        # Métricas simuladas
        df['Popularidad_TMDb'] = np.random.uniform(10, 100, size=len(df))
        df['Calificacion_Promedio_TMDb'] = np.random.uniform(5, 9, size=len(df))
        df['Cantidad_Votos_TMDb'] = np.random.randint(100, 20000, size=len(df))
        
        # Tipo de medio (70% series, 30% películas)
        df['Tipo_Medio_TMDb'] = np.random.choice(['tv', 'movie'], size=len(df), p=[0.7, 0.3])
        
        # Fecha de estreno simulada
        df['Fecha_Estreno_TMDb'] = pd.to_datetime('2015-01-01') + pd.to_timedelta(np.random.randint(0, 365*5, size=len(df)), unit='D')
        
        # Duración simulada
        df['Duracion_Minutos_TMDb'] = df['Tipo_Medio_TMDb'].apply(
            lambda x: np.random.randint(20, 60) if x == 'tv' else np.random.randint(80, 180)
        )
    else:
        # Cargar datos enriquecidos reales
        logging.info(f"Cargando datos enriquecidos desde: {ENRICHED_DATA_PATH}")
        try:
            df = pd.read_csv(ENRICHED_DATA_PATH)
            
            # Renombrar columnas si es necesario
            rename_cols = {
                'tmdb_id': 'ID_TMDb',
                'tmdb_title': 'Titulo_TMDb',
                'tmdb_genres': 'Generos_TMDb',
                'tmdb_popularity': 'Popularidad_TMDb',
                'tmdb_vote_average': 'Calificacion_Promedio_TMDb',
                'tmdb_vote_count': 'Cantidad_Votos_TMDb',
                'tmdb_media_type': 'Tipo_Medio_TMDb',
                'tmdb_release_date': 'Fecha_Estreno_TMDb',
                'tmdb_runtime_minutes': 'Duracion_Minutos_TMDb'
            }
            
            # Aplicar renombrado solo para columnas que existen
            rename_dict = {old: new for old, new in rename_cols.items() if old in df.columns}
            if rename_dict:
                df.rename(columns=rename_dict, inplace=True)
            
            logging.info(f"Datos enriquecidos cargados con {len(df)} registros")
        except Exception as e:
            logging.error(f"Error al cargar datos enriquecidos: {e}")
            return
    
    # Procesamiento de datos para Power BI
    logging.info("Procesando datos para análisis...")
    
    # Asegurarse que las fechas están en formato correcto
    for col in ['Fecha_Visualizacion', 'Fecha_Estreno_TMDb']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convertir valores numéricos
    numeric_cols = ['Popularidad_TMDb', 'Calificacion_Promedio_TMDb', 
                    'Cantidad_Votos_TMDb', 'Duracion_Minutos_TMDb']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Procesamiento de componentes temporales
    if 'Fecha_Visualizacion' in df.columns:
        df['Anio'] = df['Fecha_Visualizacion'].dt.year
        df['Mes_Num'] = df['Fecha_Visualizacion'].dt.month
        df['Dia_Mes'] = df['Fecha_Visualizacion'].dt.day
        df['Dia_Semana_Num'] = df['Fecha_Visualizacion'].dt.dayofweek  # 0=Lunes, 6=Domingo
        df['Hora_Visualizacion'] = df['Fecha_Visualizacion'].dt.hour
        df['Semana_Anio'] = df['Fecha_Visualizacion'].dt.isocalendar().week
        
        # Nombres en español para meses y días
        meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        
        df['Mes'] = df['Mes_Num'].map(meses_es)
        df['Dia_Semana'] = df['Dia_Semana_Num'].map(dias_es)
    
    # Clasificación de calidad detallada (4 niveles)
    if 'Calificacion_Promedio_TMDb' in df.columns:
        condiciones_detalladas = [
            (df['Calificacion_Promedio_TMDb'] >= 8.0),
            (df['Calificacion_Promedio_TMDb'] >= 7.0) & (df['Calificacion_Promedio_TMDb'] < 8.0),
            (df['Calificacion_Promedio_TMDb'] >= 6.0) & (df['Calificacion_Promedio_TMDb'] < 7.0),
            (df['Calificacion_Promedio_TMDb'] < 6.0)
        ]
        categorias_detalladas = ['Excelente', 'Bueno', 'Regular', 'Malo']
        df['Categoria_Calidad'] = np.select(condiciones_detalladas, categorias_detalladas, default='Sin calificación')
        
        # Clasificación simplificada de calidad (3 niveles)
        condiciones_simples = [
            (df['Calificacion_Promedio_TMDb'] >= 7.5),
            (df['Calificacion_Promedio_TMDb'] >= 6.0) & (df['Calificacion_Promedio_TMDb'] < 7.5),
            (df['Calificacion_Promedio_TMDb'] < 6.0)
        ]
        categorias_simples = ['Alta', 'Media', 'Baja']
        df['Calidad'] = np.select(condiciones_simples, categorias_simples, default='Sin calificación')
    
    # Añadir campo de Tipo Simplificado
    if 'Tipo_Medio_TMDb' in df.columns:
        df['Tipo_Medio'] = df['Tipo_Medio_TMDb']
        df['Es_Serie'] = df['Tipo_Medio_TMDb'] == 'tv'
        df['Es_Pelicula'] = df['Tipo_Medio_TMDb'] == 'movie'
    
    # Calcular tiempo desde el estreno
    if 'Fecha_Visualizacion' in df.columns and 'Fecha_Estreno_TMDb' in df.columns:
        df['Tiempo_Desde_Estreno'] = (df['Fecha_Visualizacion'] - df['Fecha_Estreno_TMDb']).dt.days
    
    # Simular tiempo de visualización si no existe
    if 'Duracion_Minutos_TMDb' in df.columns and 'Tiempo_Visualizacion' not in df.columns:
        import random
        
        def estimar_tiempo_visto(row):
            if pd.isna(row['Duracion_Minutos_TMDb']) or row['Duracion_Minutos_TMDb'] == 0:
                return None
                
            if row.get('Tipo_Medio_TMDb') == 'movie':
                # Para películas, asumimos entre 70-100% de visualización
                return round(row['Duracion_Minutos_TMDb'] * random.uniform(0.7, 1.0))
            else:
                # Para series, asumimos entre 80-100% de visualización de un episodio
                return round(row['Duracion_Minutos_TMDb'] * random.uniform(0.8, 1.0))
        
        df['Tiempo_Visualizacion'] = df.apply(estimar_tiempo_visto, axis=1)
    
    # Guardar el DataFrame principal procesado
    logging.info(f"Guardando datos procesados en: {PROCESSED_DATA_PATH}")
    try:
        df.to_csv(PROCESSED_DATA_PATH, index=False)
        logging.info(f"Datos guardados exitosamente con {len(df)} filas y {len(df.columns)} columnas")
    except Exception as e:
        logging.error(f"Error al guardar los datos procesados: {e}")
        return
    
    # Generar DataFrames adicionales para análisis específicos
    
    # 1. Crear DataFrame para análisis de calidad
    if all(col in df.columns for col in ['Tipo_Medio', 'Calidad', 'Calificacion_Promedio_TMDb']):
        logging.info("Generando archivo de promedio de calidad por tipo...")
        promedio_calidad_tipo = df.groupby('Tipo_Medio_TMDb')['Calificacion_Promedio_TMDb'].mean().reset_index()
        promedio_calidad_tipo.to_csv(CALIDAD_TIPO_PATH, index=False)
        
        logging.info("Generando archivo de resumen de calidad por tipo...")
        resumen_calidad_tipo = df.groupby(['Tipo_Medio_TMDb', 'Calidad']).size().reset_index(name='Conteo')
        resumen_calidad_tipo.to_csv(RESUMEN_CALIDAD_TIPO_PATH, index=False)
    
    # 2. Crear DataFrame para análisis de géneros
    if 'Generos_TMDb' in df.columns:
        logging.info("Generando archivos de análisis de géneros...")
        
        # Explotar la columna de géneros para crear una fila por género
        generos_dfs = []
        
        for idx, row in df.iterrows():
            generos = [g.strip() for g in str(row.get('Generos_TMDb', '')).split(',')] if pd.notna(row.get('Generos_TMDb', '')) else ['Sin género']
            
            for genero in generos:
                if genero and genero != 'Sin género':
                    genero_row = {
                        'Genero': genero,
                        'Popularidad_TMDb': row.get('Popularidad_TMDb'),
                        'Calificacion_Promedio_TMDb': row.get('Calificacion_Promedio_TMDb'),
                        'Tipo_Medio': row.get('Tipo_Medio'),
                        'Fecha_Visualizacion': row.get('Fecha_Visualizacion'),
                        'Anio': row.get('Anio'),
                        'Titulo_TMDb': row.get('Titulo_TMDb')
                    }
                    generos_dfs.append(pd.DataFrame([genero_row]))
        
        if generos_dfs:
            df_generos = pd.concat(generos_dfs, ignore_index=True)
            df_generos.to_csv(GENEROS_PATH, index=False)
            
            # Generar análisis de géneros populares
            generos_populares = df_generos.groupby('Genero').agg({
                'Popularidad_TMDb': 'mean',
                'Calificacion_Promedio_TMDb': 'mean',
                'Genero': 'count'
            }).rename(columns={'Genero': 'Conteo'}).sort_values('Conteo', ascending=False).reset_index()
            
            generos_populares.to_csv(GENEROS_POPULARES_PATH, index=False)
            
            logging.info(f"Generados {len(df_generos)} registros para análisis de géneros")
    
    logging.info("Preparación de datos para Power BI completada exitosamente")

if __name__ == "__main__":
    preparar_datos_para_powerbi()
