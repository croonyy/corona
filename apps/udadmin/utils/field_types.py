from pydantic import BaseModel, Field, conint, validator, AnyUrl
from typing import Union
from tortoise import fields

orm_fields = {
    fields.BigIntField: conint(gt=-(2**63), lt=2**63 - 1),
    fields.BinaryField: str,
    # fields.BooleanField: ,
    fields.data.BooleanField: bool,
    # fields.CharEnumField: str,
    fields.data.CharEnumFieldInstance: str,
    fields.CharField: str,
    fields.DateField: str,
    fields.DatetimeField: str,
    fields.DecimalField: float,
    fields.FloatField: float,
    fields.IntEnumField: int,
    fields.IntField: conint(gt=-(2**31), lt=2**31 - 1),
    # fields.JSONField: str,
    fields.data.JSONField: str,
    fields.SmallIntField: conint(gt=-(2**15), lt=2**15 - 1),
    fields.TextField: str,
    fields.TimeDeltaField: str,
    fields.TimeField: str,
    fields.UUIDField: str,
    # relational fields
    fields.relational.ManyToManyFieldInstance: list,
    fields.relational.ForeignKeyFieldInstance: Union[list, str],
}

map = {
    "BigIntField": None,
    "BinaryField": None,
    "BooleanField": None,
    "CharEnumFieldInstance": None,
    "CharField": None,
    "DateField": None,
    "DatetimeField": None,
    "DecimalField": None,
    "FloatField": None,
    "IntEnumField": None,
    "IntField": None,
    "JSONField": None,
    "SmallIntField": None,
    "TextField": None,
    "TimeDeltaField": None,
    "TimeField": None,
    "UUIDField": None,
    "ManyToManyFieldInstance": None,
    "ForeignKeyFieldInstance": None,
}

if __name__ == "__main__":
    from pprint import pprint

    # pprint([i.__name__ for i in type_map])
    for i in orm_fields:
        print(f'"{i.__name__}":None,')
