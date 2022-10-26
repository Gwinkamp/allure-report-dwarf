import asyncio
import services
from models import Settings
from containers import Container
from infrastructure import get_target_storage
from dependency_injector import providers
from dependency_injector.wiring import inject, Provide


@inject
async def main(
        receiver_api: services.ReceiverApi = Provide[Container.receiver_api],
        allure_report: services.AllureReport = Provide[Container.allure_report]
):
    await allure_report.restore_results()
    await asyncio.gather(
        asyncio.to_thread(receiver_api.run),
        allure_report.run_allure_report()
    )


@inject
def override_storage(
        container: Container,
        settings: Settings = Provide[Container.settings]
):
    storage_class = get_target_storage(settings.storage.type)

    container.storage.override(
        providers.Factory(
            storage_class,
            settings=container.settings,
            cache=container.cache
        )
    )


if __name__ == '__main__':
    container = Container()
    container.wire([__name__])

    override_storage(container)

    asyncio.run(main())
