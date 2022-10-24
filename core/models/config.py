import os
import config
from pathlib import Path
from pydantic import BaseModel, BaseSettings


class AllureReportConfig(BaseModel):
    host: str
    port: int
    report_dirpath: str | None


class AllureReceiverConfig(BaseModel):
    host: str
    port: int
    log_level: str


class AllureConfig(BaseModel):
    allure_path: str | None
    results_dir: str | None
    report: AllureReportConfig
    receiver: AllureReceiverConfig


class SeafileConfig(BaseModel):
    url: str
    username: str
    password: str
    allure_repo: str
    allure_dirpath: str


class Config(BaseSettings):
    allure: AllureConfig
    seafile: SeafileConfig
    temp_dir: str | None

    def get_allure_path(self) -> str:
        if not self.allure.allure_path:
            self.allure.allure_path = 'allure'
        return self.allure.allure_path

    def get_temp_dir(self) -> Path:
        if not self.temp_dir:
            self.temp_dir = config.DEFAULT_TEMP_DIR
            self._create_dir_if_not_exists(self.temp_dir)
        return Path(self.temp_dir)

    def get_results_dir(self) -> Path:
        if not self.allure.results_dir:
            self.allure.results_dir = config.DEFAULT_ALLURE_RESULTS_DIRPATH
            self._create_dir_if_not_exists(self.allure.results_dir)
        return Path(self.allure.results_dir)

    def get_report_dir(self) -> Path:
        if not self.allure.report.report_dirpath:
            self.allure.report.report_dirpath = config.DEFAULT_ALLURE_REPORT_DIRPATH
            self._create_dir_if_not_exists(self.allure.report.report_dirpath)
        return Path(self.allure.report.report_dirpath)

    def _create_dir_if_not_exists(self, dirpath: str | Path):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    class Config:
        env_nested_delimiter = '__'
