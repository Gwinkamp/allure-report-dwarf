import os
import asyncio
import aiofiles
from pathlib import Path
from zipfile import ZipFile
from models import Settings
from services import Storage


class LocalStorage(Storage):
    """Класс, инкапсулирующий методы взаимодействия с Локальным хранилищем"""

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage_path = settings.local_storage_dirpath
        self._create_storage_dir_if_doesnt_exist()

    async def save_results_package(self, package_name: str, data: bytes):
        async with aiofiles.open(self.storage_path / package_name, 'wb') as file:
            await file.write(data)

    async def restore_results(self, restore_dir: str | Path) -> bool:
        return await asyncio.to_thread(self._restore_results, restore_dir)

    def _restore_results(self, restore_dir: str | Path) -> bool:
        packages = self._find_packages_from_disk()

        if not packages:
            self._logger.warning('Пакеты с результатами отсутствуют')
            return False

        for package in packages:
            try:
                with ZipFile(package) as zf:
                    zf.extractall(restore_dir)
            except Exception as e:
                self._logger.error(f'Не удалось распаковать пакет {package}. {e}')

        return True

    def _find_packages_from_disk(self):
        packages = []
        for item in os.listdir(self.storage_path):
            path_to_item = self.storage_path / str(item)
            if os.path.isfile(path_to_item) and str(path_to_item).endswith('.zip'):
                packages.append(path_to_item)

        return packages

    def _create_storage_dir_if_doesnt_exist(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
