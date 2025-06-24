from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "configtype" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 配置类型 */,
    "name" VARCHAR(255) NOT NULL UNIQUE /* 类型名 */,
    "extra" JSON   /* 扩展 */
) /* 配置类型表 */;
CREATE TABLE IF NOT EXISTS "config" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 配置id */,
    "name" VARCHAR(255) NOT NULL UNIQUE /* 配置名 */,
    "params" JSON   /* params */,
    "extra" JSON   /* 扩展 */,
    "config_type_id" INT NOT NULL REFERENCES "configtype" ("id") ON DELETE CASCADE /* 配置类型 */
) /* 配置表 */;
CREATE TABLE IF NOT EXISTS "permissiontype" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 类型id */,
    "name" VARCHAR(255) NOT NULL UNIQUE /* 类型名 */,
    "extra" JSON   /* 扩展 */
) /* 权限类型表 */;
CREATE TABLE IF NOT EXISTS "permission" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 权限id */,
    "name" VARCHAR(255) NOT NULL UNIQUE /* 权限名 */,
    "extra" JSON   /* 扩展 */,
    "permission_type_id" INT NOT NULL REFERENCES "permissiontype" ("id") ON DELETE CASCADE /* 权限类型 */
) /* 权限表 */;
CREATE TABLE IF NOT EXISTS "role" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* #角色id# */,
    "name" VARCHAR(255) NOT NULL UNIQUE /* 角色名 */,
    "extra" JSON   /* 扩展 */
) /* 角色表 */;
CREATE TABLE IF NOT EXISTS "user" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 字段说明 */,
    "username" VARCHAR(255) NOT NULL UNIQUE /* 账号 */,
    "password" VARCHAR(255) NOT NULL  /* 密码 */,
    "gender" VARCHAR(50) NOT NULL  DEFAULT '男' /* 性别 */,
    "cn_name" VARCHAR(255)   /* 中文名 */,
    "is_delete" INT NOT NULL  DEFAULT 0 /* 是否删除 */,
    "last_login" TIMESTAMP   /* 最后登录时间 */,
    "is_superuser" INT NOT NULL  DEFAULT 0 /* 是否是超级管理员 */,
    "is_active" INT NOT NULL  DEFAULT 1 /* 是否活动状态 */
) /* 用户表 */;
CREATE TABLE IF NOT EXISTS "record" (
    "created_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 创建记录的时间 */,
    "updated_at" TIMESTAMP   DEFAULT CURRENT_TIMESTAMP /* 更新记录的时间 */,
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 操作id */,
    "name" VARCHAR(255) NOT NULL  /* 操作名称 */,
    "info" JSON   /* 记录信息 */,
    "extra" JSON   /* 扩展信息 */,
    "operate_time" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP /* 操作时间 */,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE /* 操作用户 */
) /* 操作记录表 */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "testmodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 主键id */,
    "big_int_field" BIGINT NOT NULL,
    "binary_field" BLOB NOT NULL,
    "boolean_field" INT NOT NULL,
    "char_enum_field" VARCHAR(7) NOT NULL  /* 测试枚举 */,
    "char_field" VARCHAR(255) NOT NULL  /* 字符串类型 */,
    "date_field" DATE NOT NULL  /* 日期类型 */,
    "date_time_field" TIMESTAMP NOT NULL  /* 日期时间类型 */,
    "decimal_field" VARCHAR(40) NOT NULL  /* 小数类型 */,
    "float_field" REAL NOT NULL,
    "int_enum_field" SMALLINT NOT NULL  /* 选项1: 1\n选项2: 2\n选项3: 3 */,
    "int_field" INT NOT NULL,
    "json_field" JSON NOT NULL,
    "small_integer_field" SMALLINT NOT NULL,
    "text_field" TEXT NOT NULL,
    "time_delta_field" BIGINT NOT NULL,
    "uuid_field" CHAR(36) NOT NULL
) /* 测试模型 */;
CREATE TABLE IF NOT EXISTS "role_permission" (
    "role_id" INT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "permission" ("id") ON DELETE CASCADE
) /* 角色权限表 */;
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_role_permis_role_id_7454bb" ON "role_permission" ("role_id", "permission_id");
CREATE TABLE IF NOT EXISTS "user_role" (
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE
) /* 用户角色表 */;
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_user_role_user_id_d0bad3" ON "user_role" ("user_id", "role_id");
CREATE TABLE IF NOT EXISTS "user_permission" (
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "permission" ("id") ON DELETE CASCADE
) /* 用户权限表 */;
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_user_permis_user_id_944080" ON "user_permission" ("user_id", "permission_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
