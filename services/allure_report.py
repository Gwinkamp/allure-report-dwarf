import logging
import shlex
import asyncio
from models import Settings
from .storage import Storage
from .report_generator import ReportGenerator


class AllureReport:
    """Класс, инкапсулирующий методы для управления Allure Report"""

    def __init__(
            self,
            settings: Settings,
            storage: Storage,
            report_generator: ReportGenerator):
        self._settings = settings
        self._storage = storage
        self._report_generator = report_generator
        self._run_command = self._create_run_command()
        self._logger = logging.getLogger(__name__)

    def _create_run_command(self):
        return f'{self._settings.get_allure_path()} open ' + \
               f'-h {self._settings.allure.report.host} ' + \
               f'-p {self._settings.allure.report.port} ' + \
               f'{self._settings.get_report_dir()}'

    async def run_allure_report(self):
        """Запустить Allure Report"""
        args = shlex.split(self._run_command)

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        if process.stdout:
            for stdout_coroutine in iter(process.stdout.readline, ''):
                stdout_line = await stdout_coroutine
                if stdout_line:
                    self._logger.info(stdout_line.decode()[:-1])

        if process.stderr:
            for stderr_coroutine in iter(process.stderr.readline, ''):
                stderr_line = await stderr_coroutine
                if stderr_line:
                    self._logger.error(stderr_line.decode()[:-1])

        return_code = await process.wait()

        if return_code:
            self._logger.critical('Allure Report прекратил свою работу')

    async def restore_results(self):
        """Восстановить результаты тестов из внешнего ФХД"""
        restored = await self._storage.restore_results(self._settings.get_results_dir())

        if restored:
            await self._report_generator.generate()
            self._logger.info('Результаты успешно восстановлены.')
        else:
            self._logger.info('Восстановление результатов не было произведено.')
