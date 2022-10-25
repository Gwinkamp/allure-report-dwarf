import logging
import shlex
import asyncio
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Генератор allure отчета"""

    INPUT_DIR = None
    OUTPUT_DIR = None
    GENERATE_COMMAND = str()

    @classmethod
    def setup(
            cls,
            allure_path: Path | str,
            input_dirpath: Path,
            output_dirpath: Path
    ):
        cls.INPUT_DIR = input_dirpath
        cls.OUTPUT_DIR = output_dirpath
        cls.GENERATE_COMMAND = f'{allure_path} generate -c {input_dirpath} -o {output_dirpath}'

    @classmethod
    def _unpack_data(cls, data: bytes):
        with ZipFile(BytesIO(data)) as zipped_data:
            zipped_data.extractall(cls.INPUT_DIR)

    @classmethod
    async def generate_from_package(cls, package_data: bytes):
        """Сгенерировать allure отчет из пакета с результатами"""
        cls._unpack_data(package_data)

        args = shlex.split(cls.GENERATE_COMMAND)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await cls._log_process_output(process.stdout)
        await cls._log_process_output(process.stderr)

        return_code = await process.wait()

        if return_code != 0:
            logger.error('ReportGenerator завершил свою работу с ошибками')

    @classmethod
    async def generate(cls):
        """Сгенерировать allure отчет"""
        args = shlex.split(cls.GENERATE_COMMAND)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        await cls._log_process_output(process.stdout)
        await cls._log_process_output(process.stderr)

        return_code = await process.wait()

        if return_code != 0:
            logger.error('ReportGenerator завершил свою работу с ошибками')

    @staticmethod
    async def _log_process_output(stream: asyncio.StreamReader):
        output = await stream.read()
        if output:
            logger.info(output.decode()[:-1])
