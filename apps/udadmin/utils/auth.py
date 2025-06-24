from datetime import datetime, timedelta, timezone
from typing import Annotated

# import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.security.base import SecurityBase
import asyncio

# from fastapi.openapi.models import SecurityBase
# from typing import Any, Dict, List, Optional, Union, cast
# from jwt.exceptions import InvalidTokenError
from functools import wraps
import inspect
from tortoise.expressions import Q, F
from .trans import _


from . import jwt_auth as ja
from .. import models as md

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class AuthException(Exception):
    pass


async def authenticate(username, password):
    user = await md.User.filter(username=username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"user[{username}] not exists.",
        )
    else:
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                # detail=f"password for user[{username}] is incorrect.",
                detail=_("password for user[{username}] is incorrect.").format(username=username),
            )
        return user


# user_info:{'iat': 1734080045.264618, 'exp': 1734087247.264618, 'id': 0, 'username': 'admin', 'cn_name': '管理员', 'updated_at': '2024-12-10T17:34:18.477076+08:00', 'password': '$2b$12$nQuFvms5c69eeLG07/xlS.H9cz5aevDUzoC/mzuEEgtWpzVkqOyiO', 'is_active': True, 'is_delete': False, 'created_at': '2024-12-10T17:34:18.477038+08:00', 'gender': '男', 'is_superuser': True, 'last_login': '2024-12-10T17:34:18.477122+08:00'}


async def get_user(Authorization: Annotated[str, Depends(HTTPBearer())]):
    token = Authorization.credentials
    try:
        user_info = ja.parse_payload(token)
    # except InvalidTokenError as e:
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"jwt error:class[{e.__class__.__name__}] msg[{str(e)}]",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if user_info:
    if not user_info.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"key:[username] not in credentials_info",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await md.User.filter(username=user_info["username"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user:{user_info["username"]} not exists in db",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_delete:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user:{user_info['username']} is deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user:{user_info['username']} is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def check_user_permission_async(user, perm_type, perm_name):
    perm_exists = await md.Permission.filter(
        Q(name=perm_name) & Q(permission_type__name=perm_type)
    ).exists()
    if not perm_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"perm_type[{perm_type}] perm_name[{perm_name}] not defined in db.",
        )
    user_perms = await md.Permission.filter(
        Q(name=perm_name) & Q(permission_type__name=perm_type) & Q(users__id=user.id)
    ).exists()
    # print(f"user_perms:{user_perms}")

    role_perms = await md.Permission.filter(
        Q(name=perm_name)
        & Q(permission_type__name=perm_type)
        & Q(roles__users__id=user.id)
    ).exists()
    # print(f"role_perms:{role_perms}")
    if user_perms or role_perms:
        return True
    else:
        return False


def permission_required(perm_type, perm_name):
    def inner(func):
        if inspect.iscoroutinefunction(func):  # 判断函数是不是异步函数

            @wraps(func)
            async def wrapper(*args, **kwargs):
                user = kwargs.get("user")
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated,user not found in request.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                if not user.is_superuser:
                    if await check_user_permission_async(user, perm_type, perm_name):
                        return await func(*args, **kwargs)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"user:{user.username} has no permission[{perm_type}:{perm_name}]",
                        )
                return await func(*args, **kwargs)

        else:
            # raise Exception(f"check_user_permission not support sync function")
            # 如果想要支持同步函数，则需要实现下面的check_user_permission_sync方法（同步），
            # 不能用tortoise-orm的异步方法
            # 在同步函数里面强行用异步函数check_user_permission_sync(user, perm_type, perm_name) 会返回一个awaitable对象
            # if判断会一直为真，也就是说不会判断
            # 所以需要用asyncio.run()来强制执行
            @wraps(func)
            def wrapper(*args, **kwargs):
                user = kwargs.get("user")
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated,user not found in request.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                if not user.is_superuser:
                    if asyncio.run(
                        check_user_permission_async(user, perm_type, perm_name)
                    ):
                        return func(*args, **kwargs)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"user:{user.username} has no permission[{perm_type}:{perm_name}]",
                        )
                return func(*args, **kwargs)

        return wrapper

    return inner
