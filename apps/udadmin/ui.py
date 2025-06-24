from .utils.auth import get_password_hash
from .utils.ui_tools import UiInfo
from . import models as md


user_ac = UiInfo(
    model=md.User,
    list_filter=[
        "created_at",
        "updated_at",
        "id",
        "username",
        "password",
        "gender",
        "cn_name",
        "is_delete",
        "last_login",
        "is_superuser",
        "is_active",
        "roles",
    ],
    db_value_converters={"password": get_password_hash},
    # list_display=[
    #     "username",
    #     "password",
    #     "is_active",
    #     "is_superuser",
    #     "last_login",
    # ],
    # list_display=["*"],
    # readonly_fields=["created_at", "updated_at", "last_login"],
    # json类型不支持icontain 搜索，所以relation_search中不包含json字段
    # relation_search={"roles": ["name", "id"], "permissions": ["name", "id"]},
    relation_search={"roles": ["name", "id"], "permissions": ["name", "id"]},
)
