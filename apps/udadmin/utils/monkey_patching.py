import sys
from importlib import reload

from tortoise.fields.base import Field, VALUE
from tortoise.models import ModelMeta
from tortoise import fields


mds = sys.modules


class UdModelMeta(ModelMeta):
    def __new__(cls, name, bases, dct):
        # 收集字段信息
        collected_fields = []
        for base in reversed(bases):
            if hasattr(base, "_order_fields"):
                collected_fields.extend(base._order_fields)

        order_fields = [k for k, v in dct.items() if isinstance(v, fields.Field)]
        # fs = [k for k, v in dct.items()]

        collected_fields.extend(order_fields)
        # 将收集到的属性存储在一个类属性中
        dct["_order_fields"] = collected_fields
        # 创建类对象
        return super().__new__(cls, name, bases, dct)


class UdField(Field[VALUE]):
    # aa = "aa"

    def __init__(
        self,
        *args,
        ud_order: int = 9999,
        ud_name: str = "",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ud_order = ud_order
        self.ud_name = ud_name


# 替换 tortoise.fields.base 中的 Field 类
mds["tortoise.fields.base"].Field = UdField
# reload("uvicorn")

# 重新加载依赖 Field 的模块，以确保它们使用新的 Field 类
# reload(md["tortoise.fields.base"]) # 这个不能重行加载，否则就白替换了Field
# 下面解决fetch字段的继承问题，重载顺序和是否需要重载很重要
# print("\n".join(mds.keys()))
# reload(mds["tortoise.backends"])
# reload(mds["tortoise.backends.base"])
# reload(mds["tortoise.exceptions"])
# reload(mds["tortoise.validators"])
# reload(mds["tortoise.fields.base"])
# reload(mds["tortoise.timezone"])
reload(mds["tortoise.fields.data"])
reload(mds["tortoise.fields.relational"])
reload(mds["tortoise.fields"])
reload(mds["tortoise.filters"])
reload(mds["tortoise.query_utils"])
reload(mds["tortoise.expressions"])
reload(mds["tortoise.queryset"])
# reload(mds["tortoise.log"])
# reload(mds["tortoise.utils"])
# reload(mds["tortoise.backends.base.executor"])
# reload(mds["tortoise.indexes"])
# reload(mds["tortoise.backends.base.schema_generator"])
# reload(mds["tortoise.backends.base.config_generator"])
# reload(mds["tortoise.connection"])
# reload(mds["tortoise.backends.base.client"])
# reload(mds["tortoise.router"])
# reload(mds["tortoise.manager"])
# reload(mds["tortoise.signals"])
# reload(mds["tortoise.transactions"])
reload(mds["tortoise.models"])
reload(mds["tortoise"])
# 替换 tortoise.models.Model 中的 ModelMeta 类,增加一个类属性_order_fields存储排序好的字段
mds["tortoise.models"].Model.__class__ = UdModelMeta


# mds["uvicorn.lifespan.on"].LifespanOn = UdLifespanOn
# reload(mds["uvicorn.lifespan"])


# # 测试有没有新添加的类属性
# from tortoise.fields.base import Field

# print(Field.aa)

# # CharField 继承自tortoise.fields.base.Field
# from tortoise.fields import CharField
# print(CharField.aa)

# from tortoise.fields.relational import ManyToManyFieldInstance
# print(ManyToManyFieldInstance.aa)
