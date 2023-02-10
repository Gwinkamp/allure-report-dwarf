import asyncio
from io import BytesIO
from pathlib import Path
from minio import Minio  # type: ignore
from minio.datatypes import Object  # type: ignore
from models import Settings
from services import Storage
from urllib3.response import HTTPResponse  # type: ignore


class MinioStorage(Storage):
    """Класс, инкапсулирующий методы взаимодействия с хранилищем MinIO"""

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.minio:
            raise Exception('Не определена конфигурация MinIO')
        self._config = settings.minio
        self._minio = Minio(
            endpoint=self._config.endpoint,
            access_key=self._config.access_key,
            secret_key=self._config.secret_key,
            region=self._config.region,
            secure=self._config.secure
        )

    async def save_results_package(self, package_name: str, data: bytes):
        await asyncio.to_thread(self._save_results_package, package_name, data)

    async def restore_results(self, restore_dir: str | Path) -> bool:
        return await asyncio.to_thread(self._restore_results, restore_dir)

    def _save_results_package(self, package_name: str, data: bytes):
        self._minio.put_object(
            bucket_name=self._config.bucket_name,
            object_name=f'{self._config.dirpath}/{package_name}',
            data=BytesIO(data),
            length=len(data)
        )

    def _restore_results(self, restore_dir: str | Path):
        packages = self._get_all_packages()

        if not packages:
            self._logger.warning('Пакеты с результатами отсутствуют')
            return False

        for package in packages:
            package_content = self._download_package(package)

            if not package_content:
                self._logger.error(f'Не удалось распаковать пакет {package.name}. Содержимое отсутствует')
                continue

            try:
                self._unzip_data(package_content, restore_dir)
            except Exception as e:
                self._logger.error(f'Не удалось распаковать пакет {package.name}. {e}')

        return True

    def _get_all_packages(self):
        return self._minio.list_objects(
            bucket_name=self._config.bucket_name,
            prefix=self._config.dirpath,
            recursive=True
        )

    def _download_package(self, package: Object):
        result: HTTPResponse = self._minio.get_object(
            bucket_name=self._config.bucket_name,
            object_name=package.object_name
        )
        return result.data

