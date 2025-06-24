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
    # first_name: str
    # last_name: str
    realm_roles: list
    # client_roles: list


sso = kwargs2Obj(
    server_url="http://192.168.100.197:8099",
    realm="sso-test-ldap",
    client_id="croonyy-test",
    # client_secret="cbJ1csZlvnCch8KUxgpm2TGKqoVu4RDP",
    # http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/auth?client_id=sso-test-client&redirect_uri=http://172.9.50.223:1718/rbac/sso_test&scope=openid&response_type=code
    authorization_url="http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/auth/",
    # http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/token
    token_url="http://192.168.100.197:8099/realms/sso-test-ldap/protocol/openid-connect/token/",
    # redirect_uri="http://172.9.50.223:1001/udadmin/api/v1/sso_test/",
)


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=sso.authorization_url,  # https://sso.example.com/auth/
    tokenUrl=sso.token_url,  # https://sso.example.com/auth/realms/example-realm/protocol/openid-connect/token
)

keycloak_openid = KeycloakOpenID(
    server_url=sso.server_url,  # https://sso.example.com/auth/
    client_id=sso.client_id,  # backend-client-id
    realm_name=sso.realm,  # example-realm
    # client_secret_key=sso.client_secret,  # your backend client secret
    # verify=True,
)


async def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )


# Get the payload/token from keycloak
async def get_payload(token: str = Security(oauth2_scheme)) -> dict:
    print(f"token:{token}")
    # try:
    #     return keycloak_openid.decode_token(
    #         token,
    #         key=await get_idp_public_key(),
    #         # options={"verify_signature": True, "verify_aud": False, "exp": True},
    #     )
    # except Exception as e:
    #     print(traceback.format_exc())
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail=str(e),  # "Invalid authentication credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    # key = await get_idp_public_key()
    # print(f"key:{key}")
    # key = sso.client_secret
    # key = await get_idp_public_key()
    public_key = keycloak_openid.public_key()
    print(f"public_key:{public_key}")
    # info = jwt.decode(token,key,algorithms=['HS256'])
    # info = jwt.decode(token,key,algorithms='HS256')
    # print(f"info:{info}")
    info = keycloak_openid.decode_token(
        token,
        key=public_key,
        validate=False,  # 如果client 是私密类型 需要验证客户端和client_secret 是否准确，公开类型不需要
    )
    print(f"info:")
    pprint(info)
    return info


# Get user infos from the payload
async def get_user_info(payload: dict = Depends(get_payload)) -> User:
    try:
        return User(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            # first_name=payload.get("given_name"),
            # last_name=payload.get("family_name"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
            # client_roles=payload.get("realm_access", {}).get("roles", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def test(request: Request, user: User = Depends(get_user_info)):

    print(f"request.cookies:{request.cookies}")
    return {"msg": "test"}


def sso_test(request: Request, code: str = None):
    redirect_uri = "http://172.9.50.223:1001/udadmin/api/v1/sso_test/"
    print(f"code:{code}")
    print(f"redirect_url:{redirect_uri}")
    # 如果没有code，重定向到keycloak进行登陆，完成后会重定向回来并带上code
    if not code:
        auth_url = f"{sso.authorization_url}?client_id={sso.client_id}&redirect_uri={sso.redirect_uri}&scope=openid&response_type=code"
        print(f"auth_url:{auth_url}")
        # return RedirectResponse(url=auth_url)
        headers = {
            "Location": quote(str(auth_url), safe=":/%#?=@[]!$&'()*+,;"),
        }
        return Response(headers=headers, status_code=307)
    return {"code": code}
    # return sso


def redirect_test():
    return RedirectResponse(
        url="http://172.9.50.223:1001/udadmin/api/v1/test/", status_code=302
    )


@api(
    methods=["GET"],
    tags=["Test"],
)
def cors_test(request: Request):
    print(f"request.cookies:{request.cookies}")
    headers = {
        # "Access-Control-Allow-Origin": "http://172.9.50.223:1718",
        # "Access-Control-Allow-Credentials": "true",
    }
    response = JSONResponse({"msg": "test"}, headers=headers)
    return response
