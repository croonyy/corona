from fastapi import FastAPI, Request, Query, Body

# fastapi的HTTPException是继承自StarletteHTTPException的
# 因此你可以继续像平常一样在代码中触发 FastAPI 的 HTTPException 。
# 但注册异常处理器时，应该注册到来自 Starlette 的 HTTPException。
from starlette.exceptions import HTTPException

# from fastapi import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse

# from fastapi.middleware.cors import CORSMiddleware
from fastapi import exceptions as excep
from datetime import datetime, date
from typing import Any, Union
from apps.app1 import models as md
from apps.app1 import ui
from apps.udadmin.utils.model_register import mr
from apps.udadmin.utils.decorator import timer
from apps.udadmin.utils import error_handler as eh
from apps.udadmin.utils import middleware as mw
from apps.udadmin.utils.openapi_tags import openapi_tags

from tools.timer import timer

app = FastAPI(
    # root_path="/test",
    title="app1",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    servers=[{"url": "http://localhost:1002", "description": "test"}],
    description='<img src="/static/favicon.ico" height=100>',
    # docs_url="/docs",
    debug=True,
    openapi_tags=openapi_tags,
)


# fastapi内置了一些默认的异常处理器，比如参数验证错误RequestValidationError和raise的HTTPException
# 如果需要自定义返回结构，则需要覆盖
app.exception_handler(excep.RequestValidationError)(eh.RequestValidationErrorHandler)
# token认证和权限校验都选择抛出HTTPException，能被这个错误处理器捕获
app.exception_handler(HTTPException)(eh.HttpExceptionHandler)
# 错误处理器捕获不到一般错误Exception，需要中间件全局捕获,默认是返回报错栈
# 如果不需要全局处理，就注释此行代码给需要处理的视图函数加上@eh.hand_error装饰器
app.middleware("http")(mw.CommonExceptionHandler)

# cors 配置
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:1718",
#     "http://172.9.50.223:1718",
#     "http://192.168.100.197:8099",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     # allow_origins=origins,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],f
#     allow_headers=["*"],
# )

from apps.udadmin.routes.security import router as r_security
# from .routes.test import router as r_test

# app.include_router(r_test, prefix="/test")
app.include_router(r_security, prefix="/security")

mr.register(app, md.TestModel, ui_info=ui.TestModelUi)
# mr.register(app, md.TestModel)
