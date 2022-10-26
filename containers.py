from models import Settings
from cachetools import TTLCache
from datetime import datetime, timedelta
from services import ReportGenerator
from services import Storage
from services import AllureReport
from services import ReceiverApi
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    """DI Контейнер"""

    settings = providers.Singleton(
        Settings,
        _env_file='.env'
    )

    cache = providers.Singleton(
        TTLCache,
        maxsize=16 * 1024,
        ttl=timedelta(hours=3),
        timer=datetime.now
    )

    report_generator = providers.Singleton(
        ReportGenerator,
        settings=settings
    )

    storage = providers.AbstractFactory(Storage)

    allure_report = providers.Singleton(
        AllureReport,
        settings=settings,
        storage=storage,
        report_generator=report_generator
    )

    receiver_api = providers.Singleton(
        ReceiverApi,
        settings=settings,
        storage=storage,
        report_generator=report_generator
    )
