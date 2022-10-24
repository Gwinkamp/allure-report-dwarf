from core.models import Settings
from services.report_generator import ReportGenerator
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    """DI Контейнер"""

    settings = providers.Singleton(
        Settings,
        _env_file='.env'
    )

    report_generator = providers.Singleton(ReportGenerator)
