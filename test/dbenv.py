import sys
sys.path.append('D:\\project\\fastapi_projects\\cameo')
sys.path.append('D:\\workspace\\fastapi\\cameo')

from apps.udadmin.utils import monkey_patching

from tortoise import Tortoise
from config.settings import TORTOISE_ORM


async def db_connect():
    await Tortoise.init(config = TORTOISE_ORM)


async def db_close():
    await Tortoise.close_connections()
