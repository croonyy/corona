from fastapi import APIRouter, status
from starlette.responses import JSONResponse, Response
from ..types import http_resp as hr
from ..utils import resp_code as rc
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Mapping
import json
from apps.udadmin import models as md
from tortoise import Tortoise
from apps.udadmin.utils.model_register import mr
from tools.objdoc import get_structure

# from starlette.middleware.base

router = APIRouter()


from starlette.background import BackgroundTask


# 自定义的 JSON 编码器
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # 这里使用你想要的日期格式
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


# 自定义的 JSON 响应类
class UdJSONResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            cls=CustomJSONEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# async def test():
#     # raise Exception({"status":1000, "error":"error test","msg":"msg test"})
#     now = datetime.now()
#     print(md.User._order_fields)
#     # return JSONResponse(content={"now": now}, status_code=status.HTTP_200_OK)
#     return {"now": now}
#     # return "aaa"
@router.get(
    "/test",
    tags=["Test"],
    responses=hr.general_resps,
    # response_class=UdJSONResponse,
)
async def test():
    print(Tortoise.apps)
    # print(mr.models_info)
    # get_structure(Tortoise)
    print(Tortoise.apps["udadmin"]["Config"]._meta.fields_map.keys())
    t = {
        "now": datetime.now(),
        # "models": Tortoise.apps["udadmin"]['Config']._meta.fields_map.keys(),
    }
    # print(t)
    return t
