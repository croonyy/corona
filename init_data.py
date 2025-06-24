from tortoise import Tortoise
from config.settings import TORTOISE_ORM
import traceback
from apps.udadmin import models as md
from apps.udadmin.utils.auth import pwd_context as pc
from apps.udadmin.utils.model_perms import perms
import click

apps = Tortoise.apps


async def init_db_data():
    admin, is_create_admin = await md.User.update_or_create(
        id=1,
        defaults={
            "username": "admin",
            "password": pc.hash("admin"),
            "is_superuser": True,
            "cn_name": "管理员",
        },
    )
    test_user, is_create_user2 = await md.User.update_or_create(
        id=2,
        defaults={
            "username": "test_user",
            "password": pc.hash("123456"),
            "is_superuser": False,
            "cn_name": "测试用户",
        },
    )
    modelpermtype, is_create_permtype = await md.PermissionType.update_or_create(
        id=1,
        defaults={"name": "model"},
    )

    perm_id = 0
    for app_name, models in apps.items():
        for model_name, model in models.items():
            if model_name == "Aerich":
                continue
            for perm_name, perm in perms.items():
                modelperm, is_create_modelperm = await md.Permission.update_or_create(
                    id=perm_id + 1,
                    defaults={
                        "name": f"{app_name}:{model_name.lower()}:{perm_name}",
                        "permission_type": modelpermtype,
                    },
                )
                perm_id += 1
    msg = click.style(
        f"Create 2 users: admin/admin ; test_user/123456", bold=True, fg=(0, 255, 0)
    )
    msg2 = click.style(
        f"Create {perm_id} permissions, including {list(perms.values())} model permissions",
        bold=True,
        fg=(0, 255, 0),
    )
    print(msg)
    print(msg2)


async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        await init_db_data()
    except Exception as e:
        print(traceback.format_exc())
        print(e)
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
