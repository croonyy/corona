import dbenv
from apps.udadmin import models as md
from apps.app1 import models as md1
from config import settings
from passlib.context import CryptContext
import asyncio
import traceback
from tortoise.expressions import Q, F
from apps.udadmin.utils.enums import Operate
import random
from datetime import datetime, timedelta
import uuid

from pydantic.main import create_model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pprint import pprint
from collections import OrderedDict
from tools.objdoc import get_structure
from tortoise import fields
from tortoise.models import Model
from enum import Enum

pc = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def generate_random_test_data():
    """生成n条随机测试数据"""
    for i in range(1000):
        if i % 100 == 0:
            print(f"Inserting records {i+1} to {i+100}")

        await md1.TestModel.update_or_create(
            id=i + 1,  # 从1开始的ID
            defaults={
                "big_int_field": random.randint(100000000, 999999999),
                "binary_field": b"random" + str(i + 1).encode(),
                "boolean_field": random.choice([True, False]),
                "char_enum_field": random.choice(["option1", "option2", "option3"]),
                "char_field": f"test_{i+1}",
                "date_field": (
                    datetime.now() - timedelta(days=random.randint(0, 365))
                ).strftime("%Y-%m-%d"),
                "date_time_field": (
                    datetime.now() - timedelta(hours=random.randint(0, 24))
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "decimal_field": str(random.uniform(100000000, 999999999)),
                "float_field": random.uniform(100000000, 999999999),
                "int_enum_field": random.randint(1, 3),
                "int_field": random.randint(100000000, 999999999),
                "json_field": {"key": f"value_{i+1}", "random": random.randint(1, 100)},
                "small_integer_field": random.randint(1, 100),
                "text_field": f"random text {i+1}",
                "time_delta_field": random.randint(100000000, 999999999),
                "uuid_field": str(uuid.uuid4()),
            },
        )

    for i in range(1000):
        await md.Permission.update_or_create(
            id=i + 100,  # 从1开始的ID
            defaults={
                "name": f"perm_{i+1}",
                "permission_type_id": random.randint(1, 3),
            },
        )


async def init_db_data():
    # 用户
    admin, is_create_admin = await md.User.update_or_create(
        id=1,
        defaults={
            "username": "admin",
            "password": pc.hash("admin"),
            "is_superuser": True,
            "cn_name": "管理员",
        },
    )
    user2, is_create_user2 = await md.User.update_or_create(
        id=2,
        defaults={
            "username": "user2",
            "password": pc.hash("123456"),
            "is_superuser": False,
            "cn_name": "张三",
        },
    )
    user3, is_create_user3 = await md.User.update_or_create(
        id=3,
        defaults={
            "username": "user3",
            "password": pc.hash("123456"),
            "is_superuser": False,
            "gender": "女",
            "cn_name": "李四",
        },
    )

    # 权限类型
    permtype1, is_create_permtype1 = await md.PermissionType.update_or_create(
        id=1,
        defaults={"name": "permtype1"},
    )
    permtype2, is_create_permtype2 = await md.PermissionType.update_or_create(
        id=2,
        defaults={"name": "permtype2"},
    )
    modelpermtype, is_create_permtype3 = await md.PermissionType.update_or_create(
        id=3,
        defaults={"name": "model"},
    )

    # 权限
    perm1, is_create_perm1 = await md.Permission.update_or_create(
        id=1,
        defaults={
            "name": "perm1",
            "permission_type": permtype1,
        },
    )
    perm2, is_create_perm2 = await md.Permission.update_or_create(
        id=2,
        defaults={
            "name": "perm2",
            "permission_type": permtype1,
        },
    )
    perm3, is_create_perm3 = await md.Permission.update_or_create(
        id=3,
        defaults={
            "name": "perm3",
            "permission_type": permtype2,
        },
    )
    perm_user_list, is_create_perm4 = await md.Permission.update_or_create(
        id=4,
        defaults={
            "name": "udadmin:User:list",
            "permission_type": modelpermtype,
        },
    )
    perm_user_create, is_create_perm5 = await md.Permission.update_or_create(
        id=5,
        defaults={
            "name": "udadmin:User:create",
            "permission_type": modelpermtype,
        },
    )

    # 角色
    role1, is_create_role1 = await md.Role.update_or_create(
        id=1,
        defaults={
            "name": "role1",
        },
    )
    role2, is_create_role2 = await md.Role.update_or_create(
        id=2,
        defaults={
            "name": "role2",
        },
    )
    role3, is_create_role3 = await md.Role.update_or_create(
        id=3,
        defaults={
            "name": "role3",
        },
    )

    # 配置类型
    configtype1, is_create_configtype1 = await md.ConfigType.update_or_create(
        id=1,
        defaults={
            "name": "model_manager",
        },
    )

    # 配置
    config1, is_create_config1 = await md.Config.update_or_create(
        id=1,
        defaults={
            "name": "udadmin:User",
            "config_type": configtype1,
            "params": {
                "list_display": ["*"],
                "list_filter": ["gender", "is_delete"],
                "search_fields": [],
                "readonly_fields": ["created_at", "updated_at", "last_login"],
            },
        },
    )
    config2, is_create_config2 = await md.Config.update_or_create(
        id=2,
        defaults={
            "name": "udadmin:Permission",
            "config_type": configtype1,
            "params": {
                "list_display": ["*"],
                "list_filter": [],
                "search_fields": [],
                "readonly_fields": [],
            },
        },
    )

    # 操作
    op1, is_create_op1 = await md.OperateRecord.update_or_create(
        id=1,
        defaults={
            "user": admin,
            "operate": Operate.default,
        },
    )
    op2, is_create_op2 = await md.OperateRecord.update_or_create(
        id=2,
        defaults={
            "user": user2,
            "operate": Operate.add,
        },
    )
    op3, is_create_op3 = await md.OperateRecord.update_or_create(
        id=3,
        defaults={
            "user": user3,
            "operate": Operate.delete,
        },
    )

    # 多对多关系
    await role1.permissions.add(perm1)
    await role1.permissions.add(perm_user_create)
    await role2.permissions.add(perm1)
    await role2.permissions.add(perm2)
    await role3.permissions.add(perm1)
    await role3.permissions.add(perm2)
    await role3.permissions.add(perm3)

    await user2.roles.add(role1)
    await user3.roles.add(role1)
    await user3.roles.add(role2)
    await user2.permissions.add(perm1)
    await user2.permissions.add(perm2)
    await user2.permissions.add(perm_user_list)
    await user2.permissions.add(perm_user_create)
    await user3.permissions.add(perm1)
    await user3.permissions.add(perm2)
    await user3.permissions.add(perm3)

    print(admin, user2, user3)
    print(permtype1, permtype2)
    print(perm1, perm2, perm3)
    print(role1, role2, role3)

    # 生成100条随机测试数据
    await generate_random_test_data()


async def main():
    await dbenv.db_connect()
    try:
        await init_db_data()
    except Exception as e:
        print(traceback.format_exc())
        print(e)
    finally:
        await dbenv.db_close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
