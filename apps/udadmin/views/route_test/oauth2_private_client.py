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
from pprint import pprint


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


# 视图函数
def oauth2_private_client_test(request: Request, user: User = Depends(get_user_info)):
    print(f"request.cookies:{request.cookies}")
    return {"msg": "ok", "data": user}
