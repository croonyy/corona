from fastapi import Request, Query, Form, Security, Body, Depends
from typing import Annotated

# 序列化模型
from fastapi.encoders import jsonable_encoder
from ..utils.urls import api
from ..utils import auth
from ..utils import jwt_auth as ja
from ..utils.auth import permission_required
from ..utils import error_handler as eh
from ..utils import encoder as ec
from ..utils import resp_code as rc
from ..utils import pmodels as pm
from ..types import http_resp as hr
from ..utils import field_types


@api(
    methods=["post"],
    tags=["Security"],
    responses=hr.general_resps,
)
async def login(req: pm.LoginForm):
    user = await auth.authenticate(req.username, req.password)
    user_json = jsonable_encoder(user, custom_encoder=ec.custom_encoder)
    token_info = ja.create_token(user_json)
    return {
        "code": rc.success,
        "data": token_info,
    }


@api(
    methods=["post"],
    tags=["Security"],
    responses=hr.general_resps,
)
async def refresh(request: Request, params: pm.RefreshToken):
    """
    refresh token
    """
    try:
        info = ja.parse_payload(params.refresh_token)
        # {'iat': 1737441868.4656336, 'exp': 1738737868.4656336, '_partial': True, '_custom_generated_pk': False, '_await_when_save': {}, 'password': '$2b$12$2al7PoB3s.xDaekG1KDI3eJgQqEL3f5qneygPtie7g80FLqMaUM1O', 'id': 1, 'is_delete': False, 'is_superuser': True, 'gender': '男', 'created_at': '2025-01-10 11:37:49', 'is_active': True, 'username': 'admin', 'last_login': '2025-01-10 11:37:49', 'updated_at': '2025-01-10 16:00:26', 'grant_type': 'refresh'}
        # print(info)
        if info.get("grant_type") == "refresh":
            payload = {
                k: v for k, v in info.items() if k not in ["exp", "iat", "grant_type"]
            }
            token_info = ja.create_token(payload)
            # token_info["status"] = 1
            return {
                "code": rc.success,
                "data": token_info,
            }
        else:
            raise Exception("refresh token failed. token's grant_type is not refresh")
    except Exception as e:
        raise Exception(f"refresh token failed. error:{str(e)}")


@api(
    methods=["get"],
    tags=["Security"],
)
# @eh.hand_error
def me(request: Request, user: Annotated[str, Depends(auth.get_user)]):
    return jsonable_encoder(
        {
            "code": rc.success,
            "data": user,
        },
        custom_encoder=ec.custom_encoder,
    )


@api(
    methods=["get"],
    tags=["Security"],
)
# @eh.hand_error
def get_field_types(request: Request):
    return field_types.map
