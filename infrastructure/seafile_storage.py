from io import BytesIO
from pathlib import Path
from cachetools import Cache
from models import Settings
from services.storage import Storage
from aseafile import SeafileHttpClient, SeaResult, FileItem


class SeafileStorage(Storage):
    """Класс, инкапсулирующий методы взаимодействия с Seafile"""

    DEFAULT_BASE_URL = 'http://localhost'

    def __init__(self, settings: Settings, cache: Cache, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.seafile:
            raise Exception('Не определена конфигурация для Seafile')
        self._cache = cache
        self._config = settings.seafile
        base_url = self._config.url or self.DEFAULT_BASE_URL
        self._seafile = SeafileHttpClient(base_url)

    @property
    def repo_id(self) -> str | None:
        return self._config.repo_id or self._cache.get('repo_id', None)

    @repo_id.setter
    def repo_id(self, value: str):
        self._cache['repo_id'] = value

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
            repo_id=self.repo_id or await self._get_default_repo(),
            dir_path=self._config.dirpath,
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

        packages = await self._get_all_packages()

        if not packages:
            self._logger.warning('Пакеты с результатами отсутствуют')
            return False

        for package in packages:
            package_content = await self._download_package(package)

            if not package_content:
                self._logger.error(f'Не удалось распаковать пакет {package.name}. Содержимое отсутствует')
                continue

            try:
                self._unzip_data(package_content, restore_dir)
            except Exception as e:
                self._logger.error(f'Не удалось распаковать пакет {package.name}. {e}')

        return True

    async def _obtain_token(self):
        result = await self._seafile.obtain_auth_token(self._config.username, self._config.password)
        if not result.success:
            raise Exception(
                'Не удалось получить токен в сервисе seafile. '
                f'Причина: {self._create_error_message(result)}'
            )
        self.token = result.content.token

    async def _get_default_repo(self):
        result = await self._seafile.get_default_repo(self.token)
        if not result.success:
            raise Exception(
                'Не удалось получить репозиторий по-умолчанию. '
                f'Причина: {self._create_error_message(result)}'
            )

        if result.content:
            self.repo_id = result.content
            return result.content
        else:
            raise Exception('Не удалось получить репозиторий по-умолчанию. Пустое значение')

    async def _get_all_packages(self):
        result = await self._seafile.get_files(
            repo_id=self.repo_id or await self._get_default_repo(),
            path=self._config.dirpath,
            token=self.token
        )

        if not result.success:
            self._logger.error(f'Не удалось получить информацию с ФХД. {self._create_error_message(result)}')
            return

        return result.content

    async def _download_package(self, package: FileItem):
        result = await self._seafile.download(
            repo_id=self.repo_id or await self._get_default_repo(),
            filepath=self._build_seafile_path(self._config.dirpath, package.name),
            token=self.token
        )

        if not result.success:
            self._logger.error(f'Не удалось скачать пакет {package.name}. {self._create_error_message(result)}')
            return

        return result.content

    @staticmethod
    def _create_error_message(result: SeaResult):
        if result.errors:
            return 'Ошибки: ' + '\n'.join(f'{error.title}: {error.message}' for error in result.errors)
        return

    @staticmethod
    def _build_seafile_path(dirpath: str, filename: str):
        if dirpath.endswith('/'):
            return dirpath + filename
        else:
            return dirpath + '/' + filename

