import asyncio
import services
from containers import Container
from infrastructure import SeafileClient
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


if __name__ == '__main__':
    container = Container()
    container.wire([__name__])

    container.storage.override(
        providers.Factory(
            SeafileClient,
            settings=container.settings,
            cache=container.cache
        )
    )

    asyncio.run(main())
