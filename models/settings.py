import os
import config
from pathlib import Path
from enums import StorageType
from pydantic import BaseModel, BaseSettings


def _create_dir_if_not_exists(dirpath: str | Path):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


class AllureReportConfig(BaseModel):
    host: str
    port: int
    report_dirpath: str | Path | None


class AllureReceiverConfig(BaseModel):
    host: str
    port: int


class AllureConfig(BaseModel):
    allure_path: str | Path | None
    results_dir: str | Path | None
    report: AllureReportConfig
    receiver: AllureReceiverConfig


class SeafileConfig(BaseModel):
    dirpath: str
    url: str
    username: str
    password: str
    repo_id: str


class MinioConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool
    region: str
    bucket_name: str
    dirpath: str


class Settings(BaseSettings):
    allure: AllureConfig
    storage_type: StorageType
    seafile: SeafileConfig | None
    minio: MinioConfig | None
    local_storage_dirpath: Path = config.DEFAULT_LOCAL_STORAGE_DIRPATH

    def get_allure_path(self) -> str | Path:
        if not self.allure.allure_path:
            self.allure.allure_path = 'allure'
        return self.allure.allure_path

    def get_results_dir(self) -> Path:
        if not self.allure.results_dir:
            self.allure.results_dir = config.DEFAULT_ALLURE_RESULTS_DIRPATH
            _create_dir_if_not_exists(self.allure.results_dir)
        return Path(self.allure.results_dir)

    def get_report_dir(self) -> Path:
        if not self.allure.report.report_dirpath:
            self.allure.report.report_dirpath = config.DEFAULT_ALLURE_REPORT_DIRPATH
            _create_dir_if_not_exists(self.allure.report.report_dirpath)
        return Path(self.allure.report.report_dirpath)

    class Config:
        env_nested_delimiter = '__'
