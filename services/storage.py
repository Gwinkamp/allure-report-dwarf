import logging
from io import BytesIO
from pathlib import Path
from models import Settings
from zipfile import ZipFile
from abc import ABCMeta, abstractmethod


class Storage(metaclass=ABCMeta):
    """Класс, инкапсулирующий методы взаимодействия с ФХД"""

    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    async def save_results_package(self, package_name: str, data: bytes):
        """Сохранить пакет с результатами запуска тестов

        :param package_name: имя пакета
        :param data: содержимое пакета в байтах
        """
        ...

    @abstractmethod
    async def restore_results(self, restore_dir: str | Path) -> bool:
        """Загрузить и распаковать все пакеты с ФХД в папку

        :param restore_dir: папка, куда необходимо распаковать результаты
        :return: признак того, что результаты были выгружены с ФХД
        """
        ...

    @staticmethod
    def _unzip_data(zipped_data: bytes, target_dir: str | Path):
        with ZipFile(BytesIO(zipped_data)) as zf:
            zf.extractall(target_dir)
