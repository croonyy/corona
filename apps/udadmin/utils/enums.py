from enum import Enum


class UdEnum(Enum):

    @classmethod
    def values(cls):
        return [i.value for i in cls]
    # 使用pydantic_model_creator 创建pydantic模型时，
    # fields.CharEnumField 会验证枚举值长度，因此需要定义实例对象的__len__方法
    def __len__(self):
        return len(self.value)


def create_enum_class(class_name, enum_dict):
    """
    根据字典动态创建枚举类
    :param class_name: 枚举类名
    :param enum_dict: 枚举项的字典，键为枚举项名，值为枚举项值
    :return: 枚举类
    """
    enum_members = {key: value for key, value in enum_dict.items()}
    return UdEnum(class_name, enum_members)


# Operate = Enum(
#     "Operate",
#     [
#         ("default", "default"),
#         ("add", "add"),
#         ("delete", "delete"),
#         ("update", "update"),
#         ("query", "query"),
#     ],
# )

# Gender = Enum("Gander", [("male", 1), ("female", 2)])


class Operate(UdEnum):
    default = "default"
    add = "add"
    delete = "delete"
    update = "update"
    query = "query"


class Gender(UdEnum):
    male = "男"
    female = "女"


class M2mAction(UdEnum):
    list = "list"
    # add = "add"
    # remove = "remove"
    manage = "manage"
    query = "query"

