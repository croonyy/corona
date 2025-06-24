from functools import wraps
import inspect
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field
# from typing import Optional
from fastapi import exceptions as excep
from fastapi import status
# from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
# from apps.udadmin.utils.objdoc import get_structure, pprint
from . import resp_code as rc
from config import settings

# from starlette.exceptions import HTTPException

from . import resp_code as rc

# 参考：https://mdnice.com/writing/124eac2e819343e79d532d866a615366


class udException(Exception):
    pass


# class ErrorResponse(BaseModel):
#     code: int = Field(...)
#     msg: str = Field(...)
#     data: Optional[dict] = Field(None)
#     extra: Optional[dict] = Field(None)


def hand_error(func):
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                ret = await func(*args, **kwargs)
            except Exception as e:
                trace = traceback.format_exc()
                return {
                    "code": rc.unknown_error,
                    "error": str(e),
                    "trace": str(trace),
                }
            return ret

        return wrapper
    else:

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                trace = traceback.format_exc()
                return {
                    "code": rc.unknown_error,
                    "error": str(e),
                    "trace": str(trace),
                }
            return ret

        return wrapper


async def RequestValidationErrorHandler(
    request: Request, exc: excep.RequestValidationError
):
    # 提取验证错误
    stack_trace = traceback.format_exc()
    errors = []
    errors_str = []
    for error in exc.errors():
        # 根据需要格式化错误信息
        errors.append(
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"],  # 可选，根据需要添加
                "input": error["input"],  # 可选，根据需要添加
            }
        )
        errors_str.append(str(error["loc"]) + error["msg"])
    content = {
        "code": rc.param_error,
        "msg": "Request Validation Error",
        "error": "|".join(errors_str),
        "extra": {"errors": errors},
    }
    if settings.DEBUG:
        content["trace"] = stack_trace
    # 返回自定义的 JSON 响应
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        # status_code=status.HTTP_200_OK,
        content=content,
    )


async def HttpExceptionHandler(request, exc: HTTPException) -> JSONResponse:
    """自定义处理HTTPException"""
    stack_trace = traceback.format_exc()
    content = {
        # "code": exc.status_code,
        "code": rc.http_exception,
        "msg": str(exc.detail),
        "error": f"http exception:{str(exc)}",
    }
    if settings.DEBUG:
        content["trace"] = stack_trace
    # raise Exception(content)
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )
