from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from cachetools import Cache
from models import Settings
from services.storage_client import StorageClient
from aseafile import SeafileHttpClient, SeaResult, FileItem


class SeafileClient(StorageClient):
    """Класс, инкапсулирующий методы взаимодействия с Seafile"""

    def __init__(self, settings: Settings, cache: Cache):
        super().__init__(settings)
        self._cache = cache
        self._seafile = SeafileHttpClient(settings.seafile.url)

    @property
    def token(self) -> str:
        return self._cache.get('token', None)

    @token.setter
    def token(self, value: str):
        self._cache['token'] = value

    async def save_results_package(self, package_name: str, data: bytes):
        buffer = BytesIO(data)

        if not self.token:
            await self._obtain_token()

        response = await self._seafile.upload(
            repo_id=self._config.allure_repo,
            dir_path=self._config.allure_dirpath,
            filename=package_name,
            payload=buffer,
            token=self.token
        )

        if response.success:
            self._logger.info(f'Файл {package_name} успешно сохранен на ФХД')
        else:
            self._logger.error(
                f'Не удалось сохранить файл {package_name} на ФХД. {self._create_error_message(response)}')

    async def restore_results(self, restore_dir: str | Path):
        if not self.token:
            await self._obtain_token()

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

    async def _obtain_token(self):
        result = await self._seafile.obtain_auth_token(self._config.username, self._config.password)
        if not result.success:
            self._logger.error(
                'Не удалось получить токен в сервисе seafile. '
                f'Причина: {self._create_error_message(result)}'
            )
            return
        self.token = result.content.token

    async def _get_all_packages(self):
        result = await self._seafile.get_files(
            repo_id=self._config.allure_repo,
            path=self._config.allure_dirpath,
            token=self.token
        )

        if not result.success:
            self._logger.error(f'Не удалось получить информацию с ФХД. {self._create_error_message(result)}')
            return

        return result.content

    async def _download_package(self, package: FileItem):
        result = await self._seafile.download(
            repo_id=self._config.allure_repo,
            filepath=package.name,
            token=self.token
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
            return 'Ошибки: ' + '\n'.join(f'{error.title}: {error.message}' for error in result.errors)
        return
