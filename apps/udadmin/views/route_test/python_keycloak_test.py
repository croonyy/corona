from fastapi import Request, Query
from fastapi.responses import RedirectResponse, Response, JSONResponse
from urllib.parse import quote
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID  # pip require python-keycloak
from fastapi import Security, HTTPException, status, Depends
from pydantic import BaseModel
import json
from ...utils.urls import api
from ...utils.class_tools import kwargs2Obj
import traceback
import jwt
import uuid
from pprint import pprint


# python-keycloak 文档
# https://python-keycloak.readthedocs.io/en/latest/modules/openid_client.html

# keycloak 文档
# https://article.juejin.cn/post/6844904202033086477


class User(BaseModel):
    id: str
    username: str
    email: str
    realm_roles: list


sso = kwargs2Obj(
    server_url="http://192.168.100.197:8099",
    realm="sso-test-ldap",
    client_id="croonyy-private-client",
    client_secret="IwkBciHyRVUNcbPFVXS2DTc0VVKF0AK2",  # 当client为公共访问类型的时候不会有client_secret
    # http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/auth?client_id=sso-test-client&redirect_uri=http://172.9.50.223:1718/rbac/sso_test&scope=openid&response_type=code
    authorization_url="http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/auth/",
    # http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/token
    token_url="http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/token/",
    redirect_uri="http://172.9.50.223:1001/udadmin/api/v1/call_back",
)


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=sso.authorization_url,  # https://sso.example.com/auth/
    tokenUrl=sso.token_url,  # https://sso.example.com/auth/realms/example-realm/protocol/openid-connect/token
)


keycloak_openid = KeycloakOpenID(
    server_url=sso.server_url,  # https://sso.example.com/auth/
    client_id=sso.client_id,  # backend-client-id
    realm_name=sso.realm,  # example-realm
    client_secret_key=sso.client_secret,  # your backend client secret
    # client_secret_key=sso.client_secret,  # 当client为公共访问类型的时候不会有client_secret
)


async def get_payload(token: str = Security(oauth2_scheme)) -> dict:
    info = keycloak_openid.decode_token(token)
    print(f"info:")
    pprint(info)
    return info


async def get_user_info(payload: dict = Depends(get_payload)) -> User:
    try:
        return User(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authorization Code Flow
def python_keycloak_test(request: Request):
    print(f"request.cookies:{request.cookies}")
    auth_url = keycloak_openid.auth_url(
        redirect_uri=sso.redirect_uri,
        scope="email",
        state="nicaibudao",
    )
    print(f"auth_url:{auth_url}")
    # fastapi直接重定向到不同的域名会被cors阻止，所以最好返回一个url，前端再重定向
    headers = {
        "Access-Control-Allow-Origin": "http://172.9.50.223:1001",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Credentials": "true",
    }
    return Response(
        content="Redirecting...",
        status_code=302,
        # headers={"Location": auth_url},
        headers={
            "Location": "http://172.9.50.223:1001/udadmin/api/v1/call_back?code=aa&state=aa"
        },
    )

    # return RedirectResponse(auth_url,headers=headers)
    # return {"msg": "ok", "data": auth_url}


# 身份认证回调，code 换token
def call_back(request: Request, code: str, state: str):
    # config_well_known = keycloak_openid.well_known()
    # data = {
    #     "config_well_known": config_well_known,
    # }

    access_token = keycloak_openid.token(
        grant_type="authorization_code",
        code=code,
        redirect_uri=sso.redirect_uri,
    )
    data = {
        "code": code,
        # 如果上一步存了这个state值，这一步就可以验证是不是前面的请求的回调。如果验证不通过可能是 csrf(跨站请求伪造攻击)
        "state": state,
        "access_token": access_token,
    }
    return {"msg": "ok", "data": data}


# password Flow
def python_keycloak_test_password(request: Request, username: str, password: str):
    token = keycloak_openid.token(
        grant_type="password",
        username=username,
        password=password,
        # client_secret=sso.client_secret,
        # client_id=sso.client_id,
        # realm_name=sso.realm,
        # client_secret_key=sso.client_secret,  # 当client为公共访问类型的时候不会有client_secret
    )
    # 在Keycloak中，带有权限的访问令牌被称作请求方令牌（Requesting Party Token），或者缩写为RPT。
    # token_rpt_info = keycloak_openid.introspect(
    #     keycloak_openid.introspect(
    #         token["access_token"],
    #         rpt=rpt["rpt"],
    #         token_type_hint="requesting_party_token",
    #     )
    # )
    introspect_token_info = keycloak_openid.introspect(token["access_token"])

    token_info = keycloak_openid.decode_token(token["access_token"])

    # UMA是"用户管理的授权"的缩写
    permissions = keycloak_openid.uma_permissions(token["access_token"])

    data = {
        "access_token": token,
        "info": token_info,
        "permissions": permissions,
    }
    return {"msg": "ok", "data": data}


def refresh_token(request: Request, refresh_token: str):
    access_token = keycloak_openid.token(
        grant_type="refresh_token",
        refresh_token=refresh_token,
        # client_secret=sso.client_secret,
        # client_id=sso.client_id,
        # realm_name=sso.realm,
    )
    return {"msg": "ok", "data": access_token}
