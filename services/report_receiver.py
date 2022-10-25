import uvicorn
import config
import logging.config
from uuid import uuid4
from .containers import Container
from .report_generator import ReportGenerator
from .storage_client import StorageClient
from core.models import Settings, ReceiverResponse
from dependency_injector.wiring import Provide, inject
from fastapi import (
    FastAPI,
    Depends,
    Response,
    File,
    status,
    BackgroundTasks
)


logger = logging.getLogger(__name__)
receiver = FastAPI()


@receiver.post("/upload_results")
@inject
async def upload_results(
        background_tasks: BackgroundTasks,
        response: Response,
        file: bytes = File(),
        storage: StorageClient = Depends(Provide[Container.storage]),
        report_generator: ReportGenerator = Depends(Provide[Container.report_generator])
):
    if len(file) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ReceiverResponse(
            success=False,
            message='Получены пустые данные'
        )

    zipped_filename = str(uuid4()) + '.zip'

    background_tasks.add_task(report_generator.generate_from_package, file)
    background_tasks.add_task(storage.save_results_package, zipped_filename, file)

    return ReceiverResponse(
        success=True,
        message='Результаты успешно сохранены. Отчет будет сгенерирован фоновой задачей'
    )


@inject
def run_receiver(
        settings: Settings = Provide[Container.settings],
        report_generator: ReportGenerator = Provide[Container.report_generator]
):
    report_generator.setup(
        allure_path=settings.get_allure_path(),
        input_dirpath=settings.get_results_dir(),
        output_dirpath=settings.get_report_dir()
    )

    uvicorn.run(
        receiver,
        host=settings.allure.receiver.host,
        port=settings.allure.receiver.port,
        log_config=config.logging_config_file
    )
