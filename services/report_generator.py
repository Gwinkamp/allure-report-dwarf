import os
import shlex
import asyncio
from pathlib import Path
from zipfile import ZipFile


class ReportGenerator:
    """Генератор allure отчета"""

    INPUT_DIR = None
    OUTPUT_DIR = None
    GENERATE_COMMAND = None

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
    def _unpack_data(cls, filepath: str):
        with ZipFile(filepath) as zipped_data:
            zipped_data.extractall(cls.INPUT_DIR)

    @staticmethod
    def _clear_data(filepath: str):
        os.remove(filepath)

    @classmethod
    async def generate(cls, filepath: str):
        """Сгенерировать allure отчет из"""
        cls._unpack_data(filepath)

        args = shlex.split(cls.GENERATE_COMMAND)
        process = await asyncio.create_subprocess_exec(*args)

        await process.wait()

        cls._clear_data(filepath)
