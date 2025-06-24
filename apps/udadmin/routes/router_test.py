from fastapi import APIRouter, Request
# from fastapi.openapi.utils import get_openapi
# from starlette.requests import Request
# from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
# from urllib.parse import urlparse
# from config.settings import TEMPLATES as temp
from ..utils.urls import Path

from ..views.route_test import oauth2_test as ot
from ..views.route_test import oauth2_public_client as opuc
from ..views.route_test import oauth2_private_client as oprc
from ..views.route_test import cors_test as ct 
from ..views.route_test import python_keycloak_test as pkt 


# router = APIRouter(tags=api_v1_tags)
router = APIRouter()
path = Path(router)




# path("/sso_test",ot.sso_test, tags=["Test"])
# path("/test",ot.test, tags=["Test"])
path("/oauth2_public_client_test",opuc.oauth2_public_client_test, tags=["Test"])
path("/oauth2_private_client_test",oprc.oauth2_private_client_test, tags=["Test"])
# path("/redirect_test",ot.redirect_test, tags=["Test"])
path("/cors_test",ct.cors_test, tags=["Test"])

path("/python_keycloak_test",pkt.python_keycloak_test, tags=["Test"])
path("/call_back",pkt.call_back, tags=["Test"])
path("/python_keycloak_test_password",pkt.python_keycloak_test_password, tags=["Test"])
path("/refresh_token",pkt.refresh_token, tags=["Test"])
# path("/cors_test",ot.cors_test, methods=["post"])
