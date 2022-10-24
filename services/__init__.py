from .allure_report import run_allure_report
from .report_receiver import run_receiver
from .containers import Container

container = Container()
container.wire([
    'services.report_receiver',
    'services.allure_report'
])
