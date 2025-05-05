# -*- coding: utf-8 -*-  # Esto ayuda a Python a entender caracteres especiales como tildes

# === 1. Preparando nuestras Herramientas (Importaciones) ===
import os  # Herramienta para hablar con el sistema operativo
import pandas as pd  # Herramienta para trabajar con tablas
import requests  # Herramienta para hacer peticiones web (API TMDb)
import time  # Para pausar entre llamadas a la API
from dotenv import load_dotenv  # Para leer nuestra clave API de un archivo .env
import re  # Para limpiar texto

# === 2. Instrucción Especial para Limpiar Nombres (Función) ===
def clean_netflix_title(raw_title):
    """Limpia el título crudo de Netflix para facilitar la búsqueda en API."""
    if not isinstance(raw_title, str):
        return ""
    # Divide por el primer ':' y toma la parte izquierda
    parts = raw_title.split(':', 1)
    cleaned_title = parts[0].strip()
    # Podrías añadir más reglas de limpieza aquí si es necesario
    return cleaned_title

# === 3. La Receta Principal (Nuestra Función ETL) ===
def run_etl():
    """Orquesta todo el proceso de ETL: Cargar, Limpiar, Enriquecer, Guardar."""
    print("--- ¡Hola! Voy a empezar a organizar tus datos de Netflix ---")

    # PASO 1: Preparar todo
    print("\nPASO 1: Buscando mis herramientas y secretos...")
    load_dotenv() # Carga las variables del archivo .env
    api_token = os.getenv('TMDB_API_READ_ACCESS_TOKEN') # Lee la clave API
    if not api_token:
        print("[ERROR] No encontré la clave secreta 'TMDB_API_READ_ACCESS_TOKEN' en el archivo .env.")
        return # Detiene el script si no hay clave

    # --- Estrategia de Rutas: Basada en el Directorio de Trabajo Actual ---
    # Obtenemos la carpeta desde donde se ejecutó el script (debería ser la raíz del proyecto)
    current_working_dir = os.getcwd()
    print(f"   DEBUG: Directorio de trabajo actual (desde donde ejecutaste python): {current_working_dir}")

    # Asumimos que este directorio de trabajo ES la raíz del proyecto.
    project_root = current_working_dir

    # Construimos las rutas A PARTIR de esta raíz del proyecto.
    raw_data_path = os.path.join(project_root, 'data', 'raw', 'NetflixViewingHistory.csv')
    processed_data_path = os.path.join(project_root, 'data', 'processed', 'netflix_viewing_enriched.csv')
    # --- Fin Estrategia de Rutas ---

    print(f"   Buscaré tu historial en: {raw_data_path}") # La ruta calculada
    print(f"   Guardaré el resultado final en: {processed_data_path}")
    print("   ¡Tengo la clave secreta lista!") # Confirmación de la clave

    # PASO 2: Leer historial de Netflix
    print("\nPASO 2: Abriendo tu cuaderno de historial de Netflix...")
    try:
        # Verificamos primero si el archivo existe en la ruta calculada
        if not os.path.exists(raw_data_path):
            print(f"[ERROR] El archivo NO existe en la ruta calculada: {raw_data_path}")
            print("        Asegúrate de ejecutar el script desde la carpeta raíz del proyecto ('Analisis-de_consumo_Netflix') y que el archivo esté en 'data/raw/'.")
            return # Detiene si no existe

        # Si existe, intentamos leerlo con pandas
        df_history = pd.read_csv(raw_data_path)
        print(f"   Cargado: {df_history.shape[0]} filas, {df_history.shape[1]} columnas")

        # Verificamos que las columnas necesarias estén presentes
        if 'Title' not in df_history.columns or 'Date' not in df_history.columns:
            print("[ERROR] El archivo CSV no contiene las columnas 'Title' y 'Date'.")
            return

        # Limpieza básica de datos nulos y conversión de fecha
        df_history.dropna(subset=['Title', 'Date'], inplace=True)
        df_history['Date'] = pd.to_datetime(df_history['Date'], errors='coerce')
        df_history.dropna(subset=['Date'], inplace=True)
        print(f"   Filas después de limpiar nulos y fechas inválidas: {df_history.shape[0]}")

    # Manejo de errores específicos al leer el archivo
    except FileNotFoundError:
        # Este error es menos probable ahora que usamos os.path.exists, pero por si acaso.
        print(f"[ERROR] FileNotFoundError al intentar leer con pandas: {raw_data_path}")
        return
    except Exception as e:
        print(f"[ERROR] Problema inesperado al leer o procesar el historial: {e}")
        return

    # PASO 3: Limpiar los Títulos
    print("\nPASO 3: Ordenando los nombres de las pelis y series...")
    # Aplica la función de limpieza a cada título y crea una nueva columna
    df_history['Cleaned_Title'] = df_history['Title'].apply(clean_netflix_title)
    # Obtiene una lista de títulos únicos (sin repeticiones y sin vacíos)
    unique_titles = [title for title in df_history['Cleaned_Title'].unique() if title]
    print(f"   Títulos únicos encontrados para buscar en API: {len(unique_titles)}")
    # print(f"   Algunos ejemplos: {unique_titles[:10]}") # Descomentar para ver una muestra

    # PASO 4: Enriquecimiento con API TMDb
    print(f"\nPASO 4: Contactando a TMDb para buscar información de {len(unique_titles)} títulos únicos...")
    enriched_api_data = {} # Diccionario para guardar los resultados de la API

    # Preparamos los encabezados para la API (el 'Authorization' es importante)
    headers_api = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_token}" # Usamos la clave secreta que cargamos antes
    }

    # Contador para saber cuántos títulos hemos procesado
    processed_count = 0
    titles_total = len(unique_titles)

    # Iteramos sobre cada título único que encontramos
    for title in unique_titles:
        processed_count += 1
        print(f"   [{processed_count}/{titles_total}] Buscando: '{title}'...")

        # --- 4.1: Búsqueda inicial (/search/multi) ---
        search_url = "https://api.themoviedb.org/3/search/multi"
        # Parámetros: qué buscar (query) y en qué idioma (language)
        search_params = {'query': title, 'language': 'es-ES'}
        best_match_id = None
        best_match_type = None
        api_error = False

        try:
            # Hacemos la petición a la API de búsqueda
            response_search = requests.get(search_url, params=search_params, headers=headers_api, timeout=10) # Timeout de 10 segundos
            response_search.raise_for_status() # Verifica si hubo errores HTTP (como 401, 404, etc.)
            search_results = response_search.json()

            # Buscamos el primer resultado que sea película ('movie') o serie ('tv')
            for result in search_results.get('results', []):
                media_type = result.get('media_type')
                if media_type in ['movie', 'tv']:
                    best_match_id = result.get('id')
                    best_match_type = media_type
                    # ¡Encontrado! Guardamos el ID y tipo, y salimos del bucle de resultados
                    break

            if not best_match_id:
                print(f"      -> No se encontró coincidencia relevante para '{title}'.")

        # Si hay un error al conectar con la API de búsqueda...
        except requests.exceptions.RequestException as e:
            print(f"      [ERROR API Search] Error de conexión para '{title}': {e}")
            api_error = True # Marcamos que hubo un error
        except Exception as e:
            print(f"      [ERROR Search] Error inesperado procesando búsqueda para '{title}': {e}")
            api_error = True

        # Pausa pequeña para no sobrecargar la API (¡importante!)
        time.sleep(0.4) # Esperamos 0.4 segundos antes de la siguiente acción

        # --- 4.2: Obtener Detalles (/movie/{id} o /tv/{id}) ---
        # Solo si encontramos un ID, un tipo y no hubo error antes
        if best_match_id and best_match_type and not api_error:
            details_url = f"https://api.themoviedb.org/3/{best_match_type}/{best_match_id}"
            details_params = {'language': 'es-ES'}
            details_error = False

            try:
                # Hacemos la petición para obtener los detalles
                response_details = requests.get(details_url, params=details_params, headers=headers_api, timeout=10)
                response_details.raise_for_status() # Verifica errores HTTP
                details = response_details.json()

                # --- 4.3: Extraer y Guardar Datos ---
                data_entry = {} # Diccionario para guardar los datos de ESTE título
                data_entry['tmdb_id'] = best_match_id
                data_entry['media_type'] = best_match_type

                # Título y Fecha de lanzamiento/emisión
                data_entry['fetched_title'] = details.get('title') if best_match_type == 'movie' else details.get('name')
                data_entry['release_date'] = details.get('release_date') if best_match_type == 'movie' else details.get('first_air_date')

                # Géneros (Guardamos una lista de nombres de género)
                genres_list = details.get('genres', [])
                data_entry['genres'] = [genre['name'] for genre in genres_list] if genres_list else []

                # Duración (Runtime)
                runtime = 0
                if best_match_type == 'movie':
                    runtime = details.get('runtime', 0)
                elif best_match_type == 'tv':
                    # Para series, a veces viene una lista de duraciones, tomamos la primera si existe
                    episode_runtime = details.get('episode_run_time', [])
                    if episode_runtime:
                        runtime = episode_runtime[0]
                # Nos aseguramos de que sea un número, si no, guardamos 0
                data_entry['runtime_minutes'] = runtime if isinstance(runtime, (int, float)) and runtime else 0

                # Calificación promedio en TMDb
                data_entry['vote_average'] = details.get('vote_average', 0.0)

                # Ruta del póster (solo la parte final, añadiremos el prefijo después si queremos mostrarlo)
                data_entry['poster_path'] = details.get('poster_path', '')

                # Guardamos la información extraída en nuestro diccionario principal, usando el título limpio como "llave"
                enriched_api_data[title] = data_entry
                print(f"      -> Detalles OK para '{data_entry.get('fetched_title', title)}' (ID: {best_match_id})")

            # Si hay error al obtener los detalles...
            except requests.exceptions.RequestException as e:
                print(f"      [ERROR API Details] Error de conexión para ID {best_match_id} ('{title}'): {e}")
                details_error = True
            except Exception as e:
                print(f"      [ERROR Details] Error inesperado procesando detalles para ID {best_match_id} ('{title}'): {e}")
                details_error = True

            # Pausa pequeña después de obtener detalles (si se intentó)
            if not details_error: # Solo pausamos si la llamada de detalles no falló inmediatamente
                 time.sleep(0.4)

    print(f"\n   Terminada búsqueda en API. Se obtuvo información para {len(enriched_api_data)} de {titles_total} títulos únicos.")

# --- Fin del bloque a reemplazar ---

    # PASO 5: Juntar Información (placeholder - A IMPLEMENTAR)
    print("\nPASO 5: Preparando para unir información de TMDb... (IMPLEMENTACIÓN PENDIENTE)")
    # Aquí convertiremos 'enriched_api_data' en un DataFrame y lo uniremos con 'df_history'.
    # El resultado será 'df_final'.
    df_final = df_history # ¡ESTO ES SOLO UN PLACEHOLDER!

    # PASO 6: Guardar Resultado Final (placeholder - A IMPLEMENTAR)
    print("\nPASO 6: Preparando para guardar resultado final... (IMPLEMENTACIÓN PENDIENTE)")
    # Aquí guardaremos el DataFrame 'df_final' en un archivo CSV.
    # try:
    #     df_final.to_csv(processed_data_path, index=False, encoding='utf-8')
    #     print(f"   ¡Éxito! Resultado guardado en: {processed_data_path}")
    # except Exception as e:
    #     print(f"[ERROR] No se pudo guardar el archivo final: {e}")

    print("\n--- ETL parcial completado. Falta implementar pasos 4, 5 y 6. ---")

# === 4. Punto de entrada ===
# Este bloque asegura que run_etl() se ejecute solo cuando corres el script directamente.
if __name__ == "__main__":
    run_etl()