import logging.config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

DEFAULT_ALLURE_RESULTS_DIRPATH = DATA_DIR / 'alure_results'
DEFAULT_ALLURE_REPORT_DIRPATH = DATA_DIR / 'alure_report'

DEFAULT_LOCAL_STORAGE_DIRPATH = BASE_DIR / 'backup'

# Logging
logging_config_file = 'logging.ini'
logging.config.fileConfig(logging_config_file, disable_existing_loggers=False)
