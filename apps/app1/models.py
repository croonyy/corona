from tortoise.models import Model
from tortoise import fields
from enum import Enum
from enum import IntEnum

from .utils import enums

from tortoise.fields.data import CharEnumType

app_name = "app1"  # 模型的 app名 前缀


class TestModel(Model):
    id = fields.IntField(
        pk=True, auto_increment=True, description="主键id", ud_name="序号"
    )
    big_int_field = fields.BigIntField()
    binary_field = fields.BinaryField()
    boolean_field = fields.BooleanField(ud_name="布尔类型")
    char_enum_field = fields.CharEnumField(enums.TestEnum, description="测试枚举")
    char_field = fields.CharField(max_length=255, description="字符串类型")
    date_field = fields.DateField(description="日期类型")
    date_time_field = fields.DatetimeField(description="日期时间类型")
    decimal_field = fields.DecimalField(max_digits=10, decimal_places=2, description="小数类型")
    float_field = fields.FloatField()
    # int_enum_field = fields.IntEnumField(
    #     enum_type=create_enum_class("IntTestEnum", {
    #         1: "选项1",
    #         2: "选项2",
    #         3: "选项3"
    #     })
    # )
    int_enum_field = fields.IntEnumField(
        enum_type=IntEnum("IntTestEnum", {"选项1": 1, "选项2": 2, "选项3": 3})
        # enum_type=IntEnum("IntTestEnum", {1: "选项1", 2: "选项2", 3: "选项3"})
    )
    int_field = fields.IntField()
    json_field = fields.JSONField()
    small_integer_field = fields.SmallIntField()
    text_field = fields.TextField()
    time_delta_field = fields.TimeDeltaField()
    uuid_field = fields.UUIDField()

    class Meta:
        menu_name = "test模型"
        table_description = "测试模型"
