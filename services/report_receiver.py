import uvicorn
import aiofiles
from uuid import uuid4
from .containers import Container
from .report_generator import ReportGenerator
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

receiver = FastAPI()


@receiver.post("/upload_results")
@inject
async def upload_results(
        background_tasks: BackgroundTasks,
        response: Response,
        file: bytes = File(),
        settings: Settings = Depends(Provide[Container.settings]),
        report_generator: ReportGenerator = Depends(Provide[Container.report_generator])
):
    if len(file) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ReceiverResponse(
            success=False,
            message='Получены пустые данные'
        )

    temp_dir = settings.get_temp_dir()
    zipped_filename = temp_dir / str(uuid4())

    async with aiofiles.open(zipped_filename, 'wb') as saved_file:
        await saved_file.write(file)

    background_tasks.add_task(report_generator.generate, zipped_filename)

    return ReceiverResponse(
        success=True,
        message='Результаты успешно сохранены. Отчет будет сгенерирован фоновой задачей'
    )


@inject
def run_receiver(
        config: Settings = Provide[Container.settings],
        report_generator: ReportGenerator = Provide[Container.report_generator]
):
    report_generator.setup(
        allure_path=config.get_allure_path(),
        input_dirpath=config.get_results_dir(),
        output_dirpath=config.get_report_dir()
    )

    uvicorn.run(
        receiver,
        host=config.allure.receiver.host,
        port=config.allure.receiver.port,
        log_level=config.allure.receiver.log_level
    )
