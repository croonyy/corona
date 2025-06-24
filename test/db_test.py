import dbenv
from config import settings
from passlib.context import CryptContext
import asyncio
import traceback
from tortoise.expressions import Q, F
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

pc = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def check_permission():
    # perm_exists = await md.Permission.filter(
    #     Q(name=perm_name) & Q(permission_type__name=perm_type)
    # ).exists()
    # if not perm_exists:
    #     raise Exception(
    #         f"perm_type:{perm_type} perm_name:{perm_name} not defined in db."
    #     )

    user = await md.User.get_or_none(id=2)
    perm_type = "model"
    perm_name = "perm0"

    # user_perms = await md.Permission.filter(
    #     Q(name=perm_name) & Q(permission_type__name=perm_type) & Q(users__id=user.id)
    # )
    # print(f"user_perms:{user_perms}")

    # role_perms = await md.Permission.filter(
    #     Q(name=perm_name)
    #     & Q(permission_type__name=perm_type)
    #     & Q(roles__users__id=user.id)
    # )
    # print(f"role_perms:{role_perms}")

    # perms = user_perms + role_perms

    # user_perms = await md.Permission.filter(
    #     Q(permission_type__name=perm_type) & Q(users__id=user.id)
    # )
    # role_perms = await md.Permission.filter(
    #     Q(permission_type__name=perm_type) & Q(roles__users__id=user.id)
    # )
    # print(user_perms + role_perms)

    # perms = await md.Permission.raw(
    #     f"""
    #     select
    #     a.*
    #     from ad_permission a
    #     left join ad_permission_type b on a.permission_type_id = b.id
    #     left join ad_user_permission c on a.id = c.permission_id
    #     left join ad_role_permission d on a.id = d.permission_id
    #     left join ad_user_role e on d.ad_role_id = e.role_id
    #     where 1=1
    #     and b.name = '{perm_type}'
    #     and (c.ad_user_id = {user.id} or e.ad_user_id = {user.id})
    #     """
    # )
    # print(perms,type(perms))

    q1 = await md.Permission.filter(
        Q(permission_type__name="model") & Q(users__id=user.id)
    )
    q2 = await md.Permission.filter(
        Q(permission_type__name="model") & Q(roles__users__id=user.id)
    )

    print(q1, type(q1))
    print(q2, type(q2))
    all = list(set(q1) | set(q2))
    print(all)


async def test():
    # conditions = {"username__icontains":"user2"}
    # q_final  = Q(**conditions)
    # print(q_final)
    # # q_final = Q(**conditions)
    # # q_final = Q(**conditions)
    # # Q(name="admin") & Q(email="admin@admin.com")
    # users = await md.User.filter(q_final).all().order_by().values("username",'password')
    # user = users[0]
    # print(user)

    # roles = await user.roles.all()
    # print(f"roles:{roles}")
    # print(md.User.roles.related_model)
    # print(Operate._member_map_)
    # pprint(get_structure(md.Role._meta))
    # gender = await md.User.filter().all().distinct().order_by("username").offset(0).limit(2).values("username")
    # print(gender)
    # print(md.User.all().distinct().sql())
    # print(md.User.all().distinct().values("gender", "is_superuser").sql())
    # print(await md.User.all().distinct().values("gender", "is_superuser"))
    # print(md.User._meta.db_table)
    # fields= ["gender"]
    # fields= ["gender", "is_superuser"]
    # fields_str = ",".join([f"\"{i}\"" for i in fields])
    # fields_str = ",".join([f"\"{i}\"" for i in fields])
    # sql = f"SELECT count(1) as cnt FROM (SELECT DISTINCT {fields_str} FROM {md.User._meta.db_table}) TMP"
    # sql = f"SELECT DISTINCT {fields_str} FROM {md.User._meta.db_table}"
    # sql = f"SELECT username as cnt from user where username='aaaa' "
    # sql = f"SELECT count(DISTINCT {fields_str}) cnt FROM {md.User._meta.db_table}) TMP"
    # print(sql)
    # affected_rows,rows_list = await md.User._meta.db.execute_query(sql)
    # print(affected_rows,rows_list)
    # cnt = rows_list[0]["cnt"] if rows_list else 0
    # print(cnt)
    # for row in rows_list:
    # print(dict(row))
    # query = md.User.filter()
    # print(md.User._meta.db)
    # ret = await query.raw(sql)
    # pprint(get_structure(b))
    # print(md.User.all().distinct().values("gender"))
    # print(await md.User.all().distinct().values("gender").sql)
    # fields_cn = md.User.fields_cn()
    # print(fields_cn)
    # print(md.User._meta.fields_map.get("roles"))
    # meta = md.User._meta
    # get_structure(meta)
    # get_structure(md.User._meta.fields_map.get("roles"))
    # print("="*80)
    # print(meta.fields)
    # print(meta.fields_map.keys())
    # print(meta.fields_map["username"].ud_order)
    # pprint(get_structure(meta.fields_map["username"]))
    # from tortoise import fields
    # print(fields.Field.aa)
    # print(fields.base.Field.aa)
    # print(tortoise.fields.CharField.aa)
    # print(fields.IntEnumField.aa)
    # from apps.udadmin.fields import CharField,IntEnumField,IntField
    # print(CharField.aa)
    # print(IntField.aa)
    # print(IntEnumField.aa)
    # from tortoise.fields import base
    # print(base.Field.aa)
    # from tortoise import fields
    # print(fields.IntEnumField.aa)
    # print(await md.User.filter().values())
    # ret = await md.Permission.filter(
    #             Q(permission_type__name="model")
    #             & Q(name__istartswith="udadmin:User")
    #         )
    # print(ret)
    # print(md.User._field_order)
    # print(md.User._order_fields)
    # print(md.User.Meta)
    # print(md.User._meta.fields_map)
    # a = {"last_login": "2025-02-06T10:27:00+08:00"}
    # user = await md.User.filter(id=2).first()
    # print(user)
    # print(user.last_login)
    # get_structure(md.User._meta)
    # print(md.User._meta.fields_map.keys())

    # a = {"last_login": datetime.now()}
    # a = {"last_login":  parser.parse("2025-01-23T14:17:58.895252+08:00")}
    # user.update(**a)
    # a = {"gender": "男"}
    # print(await md.User.filter(id=1).update(**a))
    # user.last_login = "2025-02-06 10:27:00"
    # user.last_login = datetime.now()
    # await user.save()

    # user = await md.User.filter(id=3).first()
    # print(getattr(md.User,"operations"))
    # print(await getattr(user,"operations").filter(id=1))
    symbol = [
        "contains",
        "icontains",
        "startswith",
        "endswith",
        "lt",
        "lte",
        "gt",
        "gte",
        "in",
        "not_in",
        "not_in",
        "isnull",
        "range",
        "not",  # 不等于
    ]
    print('|'.join([f"__{i}__" for i in symbol]))
    # user = await md1.TestModel.filter(Q(date_time_field__range=('2025-01-01', '2025-02-01')))
    # user = await md1.TestModel.filter(Q(big_int_field__contains="1")).limit(10)
    # user = await md1.TestModel.filter(Q(char_field__startswith="tes")).limit(10)
    # user = await md1.TestModel.filter(Q(char_field__endswith="10")).limit(10)
    # user = await md1.TestModel.filter(Q(small_integer_field__lte="10")).limit(10)
    # user = await md1.TestModel.filter(Q(small_integer_field__gte="10")).limit(10)
    # user = await md1.TestModel.filter(Q(small_integer_field__isnull=True)).limit(10)
    # user = await md1.TestModel.filter(Q(small_integer_field__range=(1, 10))).limit(10)
    user = await md1.TestModel.filter(Q(small_integer_field__not=30)).limit(10)
    print(user)


async def pydantic_model_creator_test():
    userin = pydantic_model_creator(
        md.User,
        name=f"{md.User}In",
        exclude_readonly=True,
    )
    obj = userin(username="user1", password="123456", is_superuser=True)
    obj.model_dump(exclude_unset=True)
    md.User.from_pydantic(obj)
    print(obj)


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
