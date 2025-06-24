import dbenv
from config import settings
from passlib.context import CryptContext
import asyncio
import traceback
from tortoise.expressions import Q, F
from tortoise.expressions import RawSQL
from apps.udadmin.utils.enums import Operate

from pydantic.main import create_model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pprint import pprint
from collections import OrderedDict
from tools.objdoc import get_structure
from tortoise import fields
from tortoise.models import Model
from datetime import datetime
from dateutil import parser
from enum import Enum
from apps.udadmin import models as md
from apps.app1 import models as md1

import random
from datetime import datetime, timedelta
import uuid

pc = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def test():
    perm = await md.Permission.filter(**{'id':1}).first()
    print(perm, await perm.permission_type)

    # 移除外键，如果有非空限制，则报错
    # perm.permission_type = None
    # await perm.save()

    perm_type1 = await md.PermissionType.filter(**{'id':1}).first()
    # print(perm_type1)
    # print(await perm_type1.permissions)
    perm_type2 = await md.PermissionType.filter(**{'id':2}).first()
    # print(perm_type2)

    # 替换外键
    perm.permission_type = perm_type2
    await perm.save()
    print(perm, await perm.permission_type)

    # await perm_type.permissions.remove(perm)


    # model = md.Permission
    # obj = await model.get(id=1)
    # get_structure(model._meta.fields_map["decimal_field"].__dict__)
    # pprint(model._meta.fields_map["decimal_field"].__dict__)
    # pprint(model._meta.fields_map["gender"].__dict__)
    # get_structure(model._meta.fields_map["binary_field"])
    # get_structure(model._meta.fields_map)
    # pprint(model._meta.fetch_fields)
    # obj = await model.filter(id=4).first()
    # print(obj)
    # print(await getattr(obj, 'permission_type'))
    # print(
    #     {
    #         f"{field.__class__.__name__}": ""
    #         for name, field in md1.TestModel._meta.fields_map.items()
    #     }
    # )
    # obj = await md.Role.filter(Q(extra__contains="a")).first()
    # print(RawSQL("json_extract(extra, '$.name') = 'John'"))
    # print(md.Role.filter(Q(extra__contains=RawSQL("json_extract(extra, '$.name') = 'John'"))).sql())
    # obj = await md.Role.filter(Q(extra__contains=RawSQL("json_extract(extra, '$.name') = 'John'"))).all()
    # print(obj)
    # get_structure(md.Permission._meta.fields_map["permission_type"].source_field)
    # print(type(md.Permission._meta.fields_map["permission_type"].source_field))
    # print(md.Permission._meta.fields_map["permission_type"].source_field)
    # print(md.OperateRecord._meta.fields_map["user"].source_field)


async def main():
    await dbenv.db_connect()
    try:
        # await check_permission()
        await test()
        # await pydantic_model_creator_test()
    except Exception as e:
        print(traceback.format_exc())
        print(e)
    finally:
        await dbenv.db_close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
