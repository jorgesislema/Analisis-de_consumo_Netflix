import unittest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from scripts.run_etl import run_netflix_etl

class TestNetflixETL(unittest.TestCase):
    def setUp(self):
        self.test_csv_content = """Title,Date
Inception,2023-01-01
Stranger Things,2023-01-02"""
        self.test_csv_path = "test_netflix_history.csv"
        with open(self.test_csv_path, "w") as f:
            f.write(self.test_csv_content)
        
        os.environ['TMDB_API_KEY'] = 'test_api_key'

    def tearDown(self):
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        if 'TMDB_API_KEY' in os.environ:
            del os.environ['TMDB_API_KEY']

    @patch('scripts.run_etl.requests.get')
    def test_api_request_failure(self, mock_get):
        mock_get.side_effect = Exception("API Error")
        with self.assertLogs(level='ERROR') as log:
            run_netflix_etl()
        self.assertTrue(any("ERROR EN PRUEBA DIRECTA" in msg for msg in log.output))

    @patch('scripts.run_etl.pd.read_csv')
    def test_invalid_csv_format(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({'WrongColumn': ['data']})
        with self.assertLogs(level='ERROR') as log:
            run_netflix_etl()
        self.assertTrue(any("El CSV debe contener 'Title' y 'Date'" in msg for msg in log.output))

    @patch('scripts.run_etl.TMDb')
    @patch('scripts.run_etl.Search')
    def test_tmdb_api_configuration_failure(self, mock_search, mock_tmdb):
        mock_tmdb.side_effect = Exception("TMDb Config Error")
        with self.assertLogs(level='ERROR') as log:
            run_netflix_etl()
        self.assertTrue(any("Error al configurar los objetos API de TMDb" in msg for msg in log.output))

    @patch('scripts.run_etl.pd.read_csv')
    def test_empty_dataframe_after_cleaning(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({
            'Title': [None, None],
            'Date': ['invalid_date', 'invalid_date']
        })
        with self.assertLogs(level='ERROR') as log:
            run_netflix_etl()
        self.assertTrue(any("No quedaron filas válidas" in msg for msg in log.output))

    @patch('scripts.run_etl.get_tmdb_details')
    @patch('scripts.run_etl.pd.read_csv')
    def test_successful_data_enrichment(self, mock_read_csv, mock_get_details):
        mock_read_csv.return_value = pd.DataFrame({
            'Title': ['Test Movie'],
            'Date': ['2023-01-01']
        })
        mock_get_details.return_value = {
            'search_title_query': 'Test Movie',
            'tmdb_id': 123,
            'title': 'Test Movie'
        }
        with self.assertLogs() as log:
            run_netflix_etl()
        self.assertTrue(any("¡Éxito! Datos enriquecidos guardados" in msg for msg in log.output))

    def test_missing_api_key(self):
        if 'TMDB_API_KEY' in os.environ:
            del os.environ['TMDB_API_KEY']
        with self.assertLogs(level='ERROR') as log:
            run_netflix_etl()
        self.assertTrue(any("No se encontró TMDB_API_KEY" in msg for msg in log.output))

    @patch('scripts.run_etl.pd.read_csv')
    def test_invalid_date_format(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({
            'Title': ['Test Movie'],
            'Date': ['01/01/2023']  # Wrong format
        })
        with self.assertLogs(level='ERROR') as log:
            run_netflix_etl()
        self.assertTrue(any("Error de formato fecha" in msg for msg in log.output))
