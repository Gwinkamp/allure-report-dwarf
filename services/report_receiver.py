import uvicorn
import config
from uuid import uuid4
from models import Settings, ReceiverResponse
from services import Storage, ReportGenerator
from fastapi import (
    FastAPI,
    APIRouter,
    Response,
    File,
    status,
    BackgroundTasks
)


class ReceiverApi:

    def __init__(
            self,
            settings: Settings,
            storage: Storage,
            report_generator: ReportGenerator):
        self._settings = settings
        self._storage = storage
        self._report_generator = report_generator
        self._api = FastAPI()
        self._router = APIRouter()
        self._register_endpoints(self._router)
        self._api.include_router(self._router)

    def _register_endpoints(self, router: APIRouter):
        router.add_api_route(
            path='/upload_results',
            endpoint=self.upload_results,
            methods=['POST']
        )

    async def upload_results(
            self,
            background_tasks: BackgroundTasks,
            response: Response,
            file: bytes = File(),
    ):
        if len(file) == 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ReceiverResponse(
                success=False,
                message='Получены пустые данные'
            )

        zipped_filename = str(uuid4()) + '.zip'

        background_tasks.add_task(self._report_generator.generate_from_package, file)
        background_tasks.add_task(self._storage.save_results_package, zipped_filename, file)

        return ReceiverResponse(
            success=True,
            message='Результаты успешно сохранены. Отчет будет сгенерирован фоновой задачей'
        )

    def run(self):
        uvicorn.run(
            self._api,
            host=self._settings.allure.receiver.host,
            port=self._settings.allure.receiver.port,
            log_config=config.logging_config_file
        )
