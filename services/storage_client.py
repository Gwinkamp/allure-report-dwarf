import logging
from pathlib import Path
from core.models import Settings
from abc import ABCMeta, abstractmethod


class StorageClient(metaclass=ABCMeta):
    """Класс, инкапсулирующий методы взаимодействия с внешним ФХД"""

    def __init__(self, settings: Settings):
        self._config = settings.seafile
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
