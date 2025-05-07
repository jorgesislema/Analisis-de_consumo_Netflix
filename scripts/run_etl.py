# --- run_etl.py ---

import pandas as pd
import os
import logging
import time
from dotenv import load_dotenv
from tmdbv3api import TMDb, Search, Movie, TV # Para la parte principal del ETL
import requests # Para la prueba directa y tmdbv3api la usa internamente
import requests.exceptions

# --- Configuración General ---
load_dotenv()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s')

# --- Constantes y Parámetros ---
EXPECTED_DATE_FORMAT = '%m/%d/%y'  # <-- ¡¡AJUSTA ESTE FORMATO!!
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
API_CALL_DELAY_SECONDS = 0.2

# --- Rutas de Archivos (Basado en la ubicación de este archivo) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'NetflixViewingHistory.csv')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'netflix_viewing_enriched.csv')
FAILED_TITLES_LOG_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'failed_api_titles.log')

# === Función para Limpiar Nombres ===
def clean_netflix_title(raw_title):
    if not isinstance(raw_title, str):
        return ""
    parts = raw_title.split(':', 1)
    cleaned_title = parts[0].strip()
    return cleaned_title

# --- Funciones Auxiliares para API (usando tmdbv3api) ---
def get_tmdb_details(title_to_search, tmdb_search_api, tmdb_movie_api, tmdb_tv_api, max_retries=MAX_RETRIES, delay_seconds=RETRY_DELAY_SECONDS):
    logging.debug(f"Procesando título para API con tmdbv3api: '{title_to_search}' (Tipo: {type(title_to_search)})")
    if not isinstance(title_to_search, str) or not title_to_search.strip():
        logging.warning(f"Título inválido o vacío proporcionado a get_tmdb_details: '{title_to_search}'. Saltando.")
        return None
    query_title = title_to_search.strip()

    for attempt in range(max_retries):
        try:
            logging.debug(f"Intento de búsqueda tmdbv3api {attempt + 1}/{max_retries} para '{query_title}'")
            search_results = tmdb_search_api.multi({'query': query_title, 'language': 'es-ES'})

            if not search_results:
                logging.info(f"No se encontró coincidencia relevante para '{query_title}' en TMDb (búsqueda tmdbv3api vacía).")
                return None
            best_result = None
            for res in search_results:
                if hasattr(res, 'media_type') and res.media_type in ['movie', 'tv']:
                    best_result = res
                    break
            if not best_result:
                logging.info(f"No se encontró coincidencia 'movie' o 'tv' para '{query_title}' (tmdbv3api).")
                return None

            media_type = best_result.media_type
            item_id = best_result.id
            tmdb_api_title = best_result.title if media_type == 'movie' else best_result.name
            logging.debug(f"Encontrado ID {item_id} ({media_type}) para '{query_title}' como '{tmdb_api_title}'. Obteniendo detalles (tmdbv3api)...")

            details = None
            if media_type == 'movie':
                details = tmdb_movie_api.details(item_id)  # Quitar language, no es soportado para películas
            elif media_type == 'tv':
                details = tmdb_tv_api.details(item_id)
            else:
                logging.warning(f"Tipo de medio '{media_type}' no soportado (tmdbv3api) para '{query_title}' (ID: {item_id}).")
                return None
            if not details:
                logging.warning(f"No se pudieron obtener detalles (tmdbv3api) para ID {item_id} ('{query_title}').")
                return None
            time.sleep(API_CALL_DELAY_SECONDS)
            details_dict = vars(details) if not isinstance(details, dict) else details
            genres_list = details_dict.get('genres', [])
            genres_str = ', '.join([genre['name'] for genre in genres_list]) if genres_list else None
            runtime_minutes = 0
            if media_type == 'movie':
                runtime_minutes = details_dict.get('runtime', 0)
            elif media_type == 'tv':
                episode_run_time = details_dict.get('episode_run_time', [])
                if episode_run_time: runtime_minutes = episode_run_time[0]
            
            extracted_data = {
                'search_title_query': title_to_search, 'tmdb_id': item_id,
                'tmdb_title': details_dict.get('title') or details_dict.get('name'),
                'tmdb_original_title': details_dict.get('original_title') or details_dict.get('original_name'),
                'tmdb_overview': details_dict.get('overview'), 'tmdb_genres': genres_str,
                'tmdb_popularity': details_dict.get('popularity'),
                'tmdb_vote_average': details_dict.get('vote_average'),
                'tmdb_vote_count': details_dict.get('vote_count'), 'tmdb_media_type': media_type,
                'tmdb_release_date': details_dict.get('release_date') if media_type == 'movie' else details_dict.get('first_air_date'),
                'tmdb_runtime_minutes': runtime_minutes if isinstance(runtime_minutes, (int, float)) and runtime_minutes else 0
            }
            logging.info(f"-> Detalles OK (tmdbv3api) para '{extracted_data['tmdb_title']}' (ID: {item_id})")
            return extracted_data
        except IndexError:
            logging.warning(f"No se encontró coincidencia relevante (IndexError en resultados tmdbv3api) para '{query_title}'.")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"[ERROR API tmdbv3api] Problema de red/conexión para '{query_title}' (Intento {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1: time.sleep(delay_seconds)
            else: logging.error(f"Reintentos tmdbv3api agotados para '{query_title}'."); return None
        except TypeError as te:
            if "quote_from_bytes" in str(te).lower() or "expected bytes" in str(te).lower():
                logging.error(f"[ERROR TypeError - quote_from_bytes tmdbv3api] para '{query_title}' (Tipo: {type(query_title)}): {te}")
            else: logging.error(f"[ERROR TypeError - OTRO tmdbv3api] para '{query_title}': {te}")
            return None
        except Exception as e:
            logging.error(f"[ERROR Inesperado tmdbv3api] en get_tmdb_details para '{query_title}' (Intento {attempt + 1}/{max_retries}): {e}")
            return None
    return None

# === La Receta Principal (Nuestra Función ETL) ===
def run_netflix_etl():
    logging.info("--- ¡Hola! Voy a empezar a organizar tus datos de Netflix ---")

    # PASO 1: Configuración y Verificación Inicial
    logging.info("PASO 1: Buscando mis herramientas y secretos...")
    if not os.path.exists(os.path.join(PROJECT_ROOT, ".env")):
        logging.warning("No se encontró archivo .env en la raíz del proyecto.")
    tmdb_api_key = os.getenv('TMDB_API_KEY')
    if not tmdb_api_key:
        logging.error("¡Error Crítico! No se encontró TMDB_API_KEY en el archivo .env o variable de entorno.")
        return
    logging.info(f"Directorio raíz del proyecto: {PROJECT_ROOT}")
    logging.info(f"Buscaré tu historial en: {RAW_DATA_PATH}")
    logging.info(f"Guardaré el resultado final en: {PROCESSED_DATA_PATH}")
    logging.info(f"Log de títulos fallidos en: {FAILED_TITLES_LOG_PATH}")

    # --- INICIO BLOQUE DE PRUEBA DIRECTA CON REQUESTS ---
    logging.info("--- Iniciando Prueba Directa con Requests (Diagnóstico) ---")
    test_title = "Inception" 
    test_search_url = f"https://api.themoviedb.org/3/search/multi"
    test_params = { 'api_key': tmdb_api_key, 'query': test_title, 'language': 'es-ES' }
    logging.debug(f"URL de prueba directa: {test_search_url}")
    logging.debug(f"Parámetros de prueba directa: {test_params}")
    try:
        response_test = requests.get(test_search_url, params=test_params, timeout=10)
        response_test.raise_for_status() 
        test_data = response_test.json()
        logging.info(f"[PRUEBA DIRECTA EXITOSA] Respuesta para '{test_title}': {test_data.get('results', [])[:1]}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR EN PRUEBA DIRECTA - RequestException] {e}")
    except TypeError as te: 
        if "quote_from_bytes" in str(te).lower() or "expected bytes" in str(te).lower():
            logging.error(f"[ERROR EN PRUEBA DIRECTA - TypeError quote_from_bytes] para '{test_title}': {te}")
        else: logging.error(f"[ERROR EN PRUEBA DIRECTA - TypeError OTRO] para '{test_title}': {te}")
    except Exception as e:
        logging.error(f"[ERROR INESPERADO EN PRUEBA DIRECTA] {e}")
    logging.info("--- Fin Prueba Directa con Requests ---")
    # --- FIN BLOQUE DE PRUEBA DIRECTA CON REQUESTS ---

    if not os.path.exists(RAW_DATA_PATH):
        logging.error(f"¡Error Crítico! No se encontró el archivo de historial después de la prueba: {RAW_DATA_PATH}")
        return

    # Configurar API de TMDb para el ETL principal
    try:
        tmdb_config = TMDb()
        tmdb_config.api_key = tmdb_api_key
        tmdb_search_api = Search()
        tmdb_movie_api = Movie()
        tmdb_tv_api = TV()
        logging.info("¡Objetos API de TMDb (tmdbv3api) listos para el ETL!")
    except Exception as e:
        logging.error(f"Error al configurar los objetos API de TMDb (tmdbv3api): {e}")
        return

    # PASO 2: Extracción y Limpieza Inicial del Historial
    logging.info("PASO 2: Abriendo tu cuaderno de historial de Netflix...")
    try:
        df_history = pd.read_csv(RAW_DATA_PATH)
        logging.info(f"Cargado: {len(df_history)} filas, {len(df_history.columns)} columnas desde {RAW_DATA_PATH}")
        if 'Title' not in df_history.columns or 'Date' not in df_history.columns:
            logging.error("El CSV debe contener 'Title' y 'Date'.")
            return
        original_rows = len(df_history)
        try:
            df_history['Date'] = pd.to_datetime(df_history['Date'], format=EXPECTED_DATE_FORMAT, errors='raise')
        except Exception:
            logging.warning(f"El formato '{EXPECTED_DATE_FORMAT}' no coincide. Intentando inferir formato automáticamente...")
            df_history['Date'] = pd.to_datetime(df_history['Date'], errors='coerce')
        df_history = df_history.dropna(subset=['Date', 'Title'])
        cleaned_rows = len(df_history)
        logging.info(f"Filas después de limpiar nulos/fechas: {cleaned_rows} (Eliminadas: {original_rows - cleaned_rows})")
        if cleaned_rows == 0: logging.error("No quedaron filas válidas."); return
    except FileNotFoundError: logging.error(f"¡Error! No se encontró archivo: {RAW_DATA_PATH}"); return
    except Exception as e: logging.error(f"Error al cargar/limpiar CSV: {e}"); return

    # PASO 3: Identificar Títulos Únicos para API
    logging.info("PASO 3: Ordenando nombres de pelis/series...")
    df_history['Title_Cleaned_For_API'] = df_history['Title'].fillna('').astype(str).apply(clean_netflix_title).str.strip()
    unique_titles_series = df_history['Title_Cleaned_For_API'].unique()
    unique_titles = [str(title) for title in unique_titles_series if pd.notna(title) and str(title).strip() != ""]
    num_unique_titles = len(unique_titles)
    if num_unique_titles == 0: logging.error("No se encontraron títulos únicos válidos."); return
    logging.info(f"Títulos únicos (strings válidos) para API: {num_unique_titles}")
    logging.debug(f"Muestra títulos únicos: {unique_titles[:5]}")

    # PASO 4: Enriquecimiento con API de TMDb
    logging.info(f"PASO 4: Contactando TMDb para {num_unique_titles} títulos...")
    tmdb_data_list = []
    failed_titles_list = []
    for title_to_search_api in unique_titles:
        details = get_tmdb_details(title_to_search_api, tmdb_search_api, tmdb_movie_api, tmdb_tv_api)
        if details: tmdb_data_list.append(details)
        else: failed_titles_list.append(title_to_search_api)
        time.sleep(API_CALL_DELAY_SECONDS)

    num_successful_api = len(tmdb_data_list)
    logging.info(f"\n--- Resumen Búsqueda API ---")
    logging.info(f"Información obtenida para {num_successful_api} de {num_unique_titles} títulos.")
    logging.info(f"No se obtuvo info para {len(failed_titles_list)} títulos.")
    if failed_titles_list:
        try:
            os.makedirs(os.path.dirname(FAILED_TITLES_LOG_PATH), exist_ok=True)
            with open(FAILED_TITLES_LOG_PATH, 'w', encoding='utf-8') as f:
                for ft in failed_titles_list: f.write(f"{ft}\n")
            logging.info(f"Lista de títulos fallidos guardada en: {FAILED_TITLES_LOG_PATH}")
        except Exception as e: logging.error(f"No se pudo guardar log de fallidos: {e}")

    # PASO 5: Unión de Datos (Merge)
    if not tmdb_data_list:
        logging.warning("No se obtuvo info de TMDb. El archivo final solo contendrá historial original.")
        df_final = df_history.copy()
        if 'Title_Cleaned_For_API' in df_final.columns:
             df_final = df_final.drop(columns=['Title_Cleaned_For_API'], errors='ignore')
    else:
        logging.info(f"PASO 5: Uniendo info de TMDb ({num_successful_api} títulos) con historial ({len(df_history)} filas)...")
        df_tmdb_data = pd.DataFrame(tmdb_data_list)
        logging.info(f"Creada tabla API con {len(df_tmdb_data)} filas y {len(df_tmdb_data.columns)} columnas.")
        logging.debug(f"Columnas en df_tmdb_data: {df_tmdb_data.columns.tolist()}")
        df_final = pd.merge(df_history, df_tmdb_data, left_on='Title_Cleaned_For_API', right_on='search_title_query', how='left')
        cols_to_drop = ['search_title_query']
        # df_final = df_final.drop(columns=['Title_Cleaned_For_API'], errors='ignore') # Mantener para revisión
        df_final = df_final.drop(columns=cols_to_drop, errors='ignore')
        logging.info(f"¡Unión completada! Tabla final: {len(df_final)} filas, {len(df_final.columns)} columnas.")
        enriched_rows = df_final['tmdb_id'].notna().sum()
        logging.info(f"Filas del historial enriquecidas: {enriched_rows} (de {len(df_history)})")
        logging.debug(f"Primeras filas df_final:\n{df_final.head()}")

    # PASO 6: Guardar Resultado Final
    logging.info(f"PASO 6: Guardando resultado final en {PROCESSED_DATA_PATH}...")
    try:
        os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
        df_final.to_csv(PROCESSED_DATA_PATH, index=False, encoding='utf-8')
        logging.info(f"¡Éxito! Datos enriquecidos guardados.")
    except Exception as e:
        logging.error(f"Error al guardar CSV final: {e}")
    logging.info("\n--- Proceso ETL completado ---")

if __name__ == "__main__":
    run_netflix_etl()