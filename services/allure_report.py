import logging
import shlex
import asyncio
from core.models import Settings
from .containers import Container
from .storage_client import StorageClient
from .report_generator import ReportGenerator
from dependency_injector.wiring import Provide, inject

logger = logging.getLogger(__name__)


@inject
async def run_allure_report(settings: Settings = Provide[Container.settings]):
    await restore_results(settings)

    args = shlex.split(f'{settings.get_allure_path()} open '
                       f'-h {settings.allure.report.host} '
                       f'-p {settings.allure.report.port} '
                       f'{settings.get_report_dir()}')

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    if process.stdout:
        for stdout_coroutine in iter(process.stdout.readline, ''):
            stdout_line = await stdout_coroutine
            if stdout_line:
                logger.info(stdout_line.decode()[:-1])

    if process.stderr:
        for stderr_coroutine in iter(process.stderr.readline, ''):
            stderr_line = await stderr_coroutine
            if stderr_line:
                logger.error(stderr_line.decode()[:-1])

    return_code = await process.wait()

    if return_code:
        logger.critical('Allure Report прекратил свою работу')


@inject
async def restore_results(
        settings: Settings,
        storage: StorageClient = Provide[Container.storage],
        report_generator: ReportGenerator = Provide[Container.report_generator]
):
    """Восстановить результаты тестов из внешнего ФХД"""
    restored = await storage.restore_results(settings.get_results_dir())

    if restored:
        await report_generator.generate()
        logger.info('Результаты успешно восстановлены.')
    else:
        logger.info('Восстановление результатов не было произведено.')
