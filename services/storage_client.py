import logging
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from core.models import Settings
from aseafile import SeafileHttpClient, SeaResult, FileItem


class StorageClient:
    """Класс, инкапсулирующий методы взаимодействия с внешним ФХД"""

    def __init__(self, settings: Settings):
        self._config = settings.seafile
        self._seafile = SeafileHttpClient(settings.seafile.url)
        self._logger = logging.getLogger(__name__)

    async def authorize(self):
        await self._seafile.authorize(self._config.username, self._config.password)

    async def save_results(self, filename: str, data: bytes):
        buffer = BytesIO(data)
        response = await self._seafile.upload(
            repo_id=self._config.allure_repo,
            dir_path=self._config.allure_dirpath,
            filename=filename,
            payload=buffer
        )

        if response.success:
            self._logger.info(f'Файл {filename} успешно сохранен на ФХД')
        else:
            self._logger.error(f'Не удалось сохранить файл {filename} на ФХД. {self._create_error_message(response)}')

    async def restore_results(self, restore_dir: str | Path):
        pakages = await self._get_all_packages()

        if not pakages:
            self._logger.warning('Пакеты с результатами отсутствуют')
            return False

        for package in pakages:
            package_content = await self._download_package(package)

            if not package_content:
                return

            try:
                self._unzip_data(package_content, restore_dir)
            except Exception as e:
                self._logger.error(f'Не удалось распаковать пакет {package.name}. {e}')

        return True

    async def _get_all_packages(self):
        result = await self._seafile.get_files(
            repo_id=self._config.allure_repo,
            path=self._config.allure_dirpath
        )

        if not result.success:
            self._logger.error(f'Не удалось получить информацию с ФХД. {self._create_error_message(result)}')
            return

        return result.content

    async def _download_package(self, package: FileItem):
        result = await self._seafile.download(
            repo_id=self._config.allure_repo,
            filepath=package.name
        )

        if not result.success:
            self._logger.error(f'Не удалось скачать пакет {package.name}. {self._create_error_message(result)}')
            return

        return result.content

    def _unzip_data(self, zipped_data: bytes, target_dir: str | Path):
        with ZipFile(BytesIO(zipped_data)) as zf:
            zf.extractall(target_dir)

    def _create_error_message(self, result: SeaResult):
        if result.errors:
            return 'Ошибки:' + '\n'.join(f'{error.title}: {error.message}' for error in result.errors)
        return
