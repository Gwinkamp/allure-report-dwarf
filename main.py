import asyncio
from services import run_allure_report, run_receiver


async def main():
    await asyncio.gather(
        asyncio.to_thread(run_receiver),
        run_allure_report()
    )


if __name__ == '__main__':
    asyncio.run(main())
