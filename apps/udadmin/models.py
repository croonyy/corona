from tortoise.models import Model
from tortoise import fields

# from ..udadmin import fields
from .utils import enums

from tortoise.fields.data import CharEnumType

app_name = "udadmin"  # 模型的 app名 前缀


# class DtBase(Model, metaclass=ModelMeta):
class DtBase(Model):
    created_at = fields.DatetimeField(
        auto_now_add=True,  # 创建记录的时候自动设置时间
        description="创建记录的时间",
        blank=True,
        null=True,
        ud_name="创建时间",
        ud_order=998,
    )
    updated_at = fields.DatetimeField(
        auto_now=True,  # 修改记录的时候自动设置时间
        description="更新记录的时间",
        blank=True,
        null=True,
        ud_name="更新时间",
        ud_order=999,
    )

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    class Meta:
        abstract = True  # 设置为抽象模型


class User(DtBase):
    """用户表"""

    id = fields.IntField(
        pk=True,
        auto_increment=True,
        description="字段说明",
        ud_name="用户ID",
        ud_order=1,
    )
    username = fields.CharField(
        max_length=255,
        unique=True,
        description="账号",
        ud_name="账号",
        ud_order=2,
    )
    # username = fields.CharField(max_length=255, unique=True, ud_name='aaa')
    password = fields.CharField(
        max_length=255,
        description="明文输入密码，保存后变成密文。",
        ud_name="密码",
        ud_order=3,
    )
    gender = fields.CharEnumField(
        enums.Gender,
        max_length=50,
        description="性别",
        ud_name="性别",
        ud_order=4,
        default=enums.Gender.male.value,
    )
    cn_name = fields.CharField(
        max_length=255,
        description="中文名",
        ud_name="中文名",
        ud_order=5,
        blank=True,
        null=True,
    )
    is_delete = fields.BooleanField(
        default=False,
        description="是否删除",
        ud_name="是否删除",
        ud_order=6,
    )
    last_login = fields.DatetimeField(
        description="最后登录时间",
        ud_name="最后登录",
        ud_order=7,
        # auto_now_add=True,
        blank=True,
        null=True,
    )
    is_superuser = fields.BooleanField(
        default=False,
        description="是否是超级管理员",
        ud_name="超级管理员",
        ud_order=8,
    )
    is_active = fields.BooleanField(
        default=True,
        description="是否活动状态",
        ud_name="活动状态",
        ud_order=9,
    )
    roles = fields.ManyToManyField(
        f"{app_name}.Role",
        related_name="users",
        # through="ad_user_role",
        description="用户角色表",
        ud_name="用户角色",
        # ud_order=10,
        blank=True,
        null=True,
    )
    # operations: fields.ReverseRelation["OperateRecord"]
    # operations = fields.ReverseRelation["OperateRecord"]
    # operations = fields.ReverseRelation(
    #     f"{app_name}.OperateRecord",
    # blank=True,
    # null=True,
    # )
    permissions = fields.ManyToManyField(
        f"{app_name}.Permission",
        related_name="users",
        # through="ad_user_permission",
        description="用户权限表",
        ud_name="用户权限",
        # ud_order=11,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.id}:{self.username}"

    class Meta:
        # ...
        menu_name = "用户管理"
        icon = "antd:TeamOutlined"
        # db = ""
        # table = "ad_user"  # 数据库中的表名称
        table_description = "用户表"


class Role(DtBase):
    """角色表"""

    id = fields.IntField(pk=True, auto_increment=True, description="#角色id#")
    name = fields.CharField(max_length=255, unique=True, description="角色名")
    extra = fields.JSONField(blank=True, null=True, description="扩展")
    permissions = fields.ManyToManyField(
        f"{app_name}.Permission",
        related_name="roles",
        # through="ad_role_permission",
        description="角色权限表",
        blank=True,
        null=True,
    )
    # users: fields.ManyToManyRelation[User]

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"

    class Meta:
        menu_name = "角色管理"
        # ud_app = 'app2'
        icon = "antd:StarOutlined"
        # table = "ad_role"  # 数据库中的表名称
        table_description = "角色表"


class PermissionType(DtBase):
    """权限类型表"""

    id = fields.IntField(pk=True, auto_increment=True, description="类型id")
    name = fields.CharField(max_length=255, unique=True, description="类型名")
    extra = fields.JSONField(blank=True, null=True, description="扩展")
    # permissions: fields.ReverseRelation["Permission"]

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"

    class Meta:
        # table = "ad_permission_type"  # 数据库中的表名称
        icon = "antd:TagFilled"
        menu_name = "权限类型"
        table_description = "权限类型表"


class Permission(DtBase):
    """权限表"""

    id = fields.IntField(pk=True, auto_increment=True, description="权限id")
    name = fields.CharField(max_length=255, unique=True, description="权限名")
    permission_type = fields.ForeignKeyField(
        f"{app_name}.PermissionType",
        related_name="permissions",
        on_delete=fields.CASCADE,
        description="权限类型",
        ud_name="权限类型对象",
    )
    extra = fields.JSONField(blank=True, null=True, description="扩展")
    # roles: fields.ManyToManyRelation[Role]
    # users: fields.ManyToManyRelation[User]

    def __str__(self) -> str:
        # return f"<{self.__class__.__name__}: {self.id}>"
        return f"<{self.id}:{self.name}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    class Meta:
        # table = "ad_permission"  # 数据库中的表名称
        icon = "antd:TagsFilled"
        menu_name = "权限实例"
        table_description = "权限表"


class ConfigType(DtBase):
    """配置类型表"""

    id = fields.IntField(pk=True, auto_increment=True, description="配置类型")
    name = fields.CharField(max_length=255, unique=True, description="类型名")
    extra = fields.JSONField(blank=True, null=True, description="扩展")

    class Meta:
        # table = "ad_permission_type"  # 数据库中的表名称
        icon = "antd:BuildFilled"
        menu_name = "配置类型管理"
        table_description = "配置类型表"


class Config(DtBase):
    """配置表"""

    id = fields.IntField(pk=True, auto_increment=True, description="配置id")
    name = fields.CharField(max_length=255, unique=True, description="配置名")
    config_type = fields.ForeignKeyField(
        f"{app_name}.ConfigType",
        related_name="configs",
        on_delete=fields.CASCADE,
        description="配置类型",
    )
    params = fields.JSONField(blank=True, null=True, description="params")
    extra = fields.JSONField(blank=True, null=True, description="扩展")

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    class Meta:
        # table = "ad_permission"  # 数据库中的表名称
        icon = "antd:SettingFilled"
        menu_name = "配置管理"
        table_description = "配置表"


class Record(DtBase):
    """操作记录表"""

    id = fields.IntField(
        pk=True, auto_increment=True, description="操作id", required=True
    )
    # operate = fields.CharEnumField(
    #     enums.Operate, description="操作", default=enums.Operate.query
    # )
    name = fields.CharField(max_length=255, description="操作名称")
    info = fields.JSONField(blank=True, null=True, description="记录信息")
    extra = fields.JSONField(blank=True, null=True, description="扩展信息")
    user = fields.ForeignKeyField(
        f"{app_name}.User", related_name="operations", description="操作用户"
    )

    operate_time = fields.DatetimeField(
        auto_now_add=True,  # 创建记录的时候自动设置时间
        description="操作时间",
        blank=True,
        null=True,
        ud_name="操作时间",
    )

    class Meta:
        # table = "ad_operate_record"  # 数据库中的表名称
        icon = "antd:ToolOutlined"
        menu_name = "操作记录"
        table_description = "操作记录表"
