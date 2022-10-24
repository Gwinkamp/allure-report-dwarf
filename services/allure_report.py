import shlex
import asyncio
from core.models import Config
from .containers import Container
from dependency_injector.wiring import Provide, inject


@inject
async def run_allure_report(config: Config = Provide[Container.config]):
    args = shlex.split(f'{config.get_allure_path()} open {config.get_report_dir()}')

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    out, err = await process.communicate()
    print('[code]: ' + str(process.returncode))
    print('[out]: ' + out.decode('utf-8'))
    print('[err]: ' + err.decode('urf-8'))
