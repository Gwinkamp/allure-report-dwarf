from .allure_report import run_allure_report
from .report_receiver import run_receiver
from .containers import Container
from infrastructure import SeafileClient
from dependency_injector import containers, providers

container = Container()
container.wire([
    'services.report_receiver',
    'services.allure_report'
])

container.storage.override(
    providers.Factory(
        SeafileClient,
        settings=container.settings,
        cache=container.cache
    )
)
