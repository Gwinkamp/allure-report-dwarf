from core.models import Settings
from cachetools import TTLCache
from datetime import datetime, timedelta
from services.report_generator import ReportGenerator
from services.storage_client import StorageClient
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

    report_generator = providers.Singleton(ReportGenerator)

    storage = providers.AbstractFactory(StorageClient)
