import logging
import shlex
import asyncio
from io import BytesIO
from zipfile import ZipFile
from models import Settings

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Генератор allure отчета"""

    def __init__(self, settings: Settings):
        self.input_dir = settings.get_results_dir()
        self.output_dir = settings.get_report_dir()
        self.generate_command = f'{settings.get_allure_path()} generate -c {self.input_dir} -o {self.output_dir}'

    def _unpack_data(self, data: bytes):
        with ZipFile(BytesIO(data)) as zipped_data:
            zipped_data.extractall(self.input_dir)

    async def generate_from_package(self, package_data: bytes):
        """Сгенерировать allure отчет из пакета с результатами"""
        self._unpack_data(package_data)

        args = shlex.split(self.generate_command)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await self._log_process_output(process.stdout)
        await self._log_process_output(process.stderr)

        return_code = await process.wait()

        if return_code != 0:
            logger.error('ReportGenerator завершил свою работу с ошибками')

    async def generate(self):
        """Сгенерировать allure отчет"""
        args = shlex.split(self.generate_command)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await self._log_process_output(process.stdout)
        await self._log_process_output(process.stderr)

        return_code = await process.wait()

        if return_code != 0:
            logger.error('ReportGenerator завершил свою работу с ошибками')

    @staticmethod
    async def _log_process_output(stream: asyncio.StreamReader | None):
        if stream is not None:
            output = await stream.read()
            if output:
                logger.info(output.decode()[:-1])
