from starlette.templating import Jinja2Templates
import os

BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

DEBUG = True
# DEBUG = False

TEMPLATES = Jinja2Templates(directory="templates")

TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://db/db.sqlite3",
        # "udadmin":"mysql://root:123456@localhost:3306/cameo",
    },
    "apps": {
        "udadmin": {
            "models": ["apps.udadmin.models", "aerich.models"],
            "default_connection": "default",
        },
        "app1": {
            # 数据库是同一个不要加aerich.models 会报错RuntimeWarning: Module "aerich.models" has no models
            # 如果数据库是不同的，没有测试，估计要加上aerich.models
            # "models": ["apps.app1.models", "aerich.models"], 
            "models": ["apps.app1.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}

# app的前端显示配置
APP_INFO = {
    "udadmin": {
        "app_name": "udadmin",
        "app_menu_name": "授权与认证",
        "app_description": "授权与认证,用户管理,角色管理,权限管理",
        "app_icon": "antd:UserOutlined",
    },
    "app1": {
        "app_name": "app1",
        "app_menu_name": "应用1",
        "app_description": "应用1,测试描述",
        "app_icon": "antd:AppstoreOutlined",
    },
    "app2": {
        "app_name": "app2",
        "app_menu_name": "应用2",
        "app_description": "应用2,测试描述",
        "app_icon": "antd:BlockOutlined",
    },
}

SECRET_KEY = "change_to_your_secret_key_here_ghbjgtimngv"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 30 # 30分钟
REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 15 # 15天


# LANGUAGE = 'en'  # 默认语言为英文
LANGUAGE = 'zh'  # 默认语言为英文

# SWAGGER_PATH='swagger_docs.html'
# REDOC_PATH='re_docs.html'

# 本地配置覆盖
try:
    from .local_settings import *

    # print(f"import settings from local_settings.py")
except Exception as e:
    # print(f"Can't import settings from local_settings.py")
    pass