from core.models import Config
from services.report_generator import ReportGenerator
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    """DI Контейнер"""

    config = providers.Singleton(
        Config,
        _env_file='.env'
    )

    report_generator = providers.Singleton(ReportGenerator)
