from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

DEFAULT_TEMP_DIR = DATA_DIR / 'temp'
DEFAULT_ALLURE_RESULTS_DIRPATH = DATA_DIR / 'alure_results'
DEFAULT_ALLURE_REPORT_DIRPATH = DATA_DIR / 'alure_report'

