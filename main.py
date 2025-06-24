# 猴子补丁，扩展tortoise.fields.Field 类，和tortoise.models.Model类
from apps.udadmin.utils import monkey_patching
from apps.udadmin.utils import logo_letters  # 打印logo
from apps.udadmin.utils import ud_doc  # 自定义swagger文档的静态文件本地加载

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

# from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from tortoise import Tortoise
from config.settings import TORTOISE_ORM
import time
from fastapi.middleware.cors import CORSMiddleware
from apps.udadmin.utils.decorator import timer
from fastapi.logger import logger


# 上下文管理loggingartup执行yield之前的代码，shutdown执行yield以下的代码
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 传递 TORTOISE_ORM 配置给 Tortoise.init()
    await Tortoise.init(config=TORTOISE_ORM)
    # 确保所有的模型都被创建（如果需要）,取消注释项目启动会自己创建，也可以用aerich init-db生成迁移文件并创建，或者用迁移文件aerich upgrade创建。
    # await Tortoise.generate_schemas()
    # 初始化数据库配置后，再注册模型，不然会找不到模型的app属性（因为app属性是在数据库init里面设置的）
    # 挂载app,也要在数据库配置初始化之后，才能有模型的app名称
    # 先从数据库获取信息配置，再挂载app（app里面会注册模型，才能拿到配置信息）
    from apps.udadmin.app import app as admin_app
    from apps.app1.app import app as app1

    app.mount("/udadmin", admin_app, name="admin")
    app.mount("/app1", app1, name="app1")

    from apps.udadmin.utils.model_register import mr

    print(f"registered models:\n{list(mr.models_info.keys())}")

    yield
    # 销毁fastapi实例后断开数据库连接
    await Tortoise.close_connections()


app = FastAPI(
    title="title",
    lifespan=lifespan,
    # root_path="/test", # 除了openapi文档地址，将服务所有的路由加上前缀才能访问。主文档地址是下面设置的，不会影响主应用文档前缀，但是会影响子应用的文档地址
    # 如果配置的不是本身文档所在的域 会导致跨域问题
    # servers=[{"url": "http://localhost:1002", "description": "test"}],  # 服务器配置
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# @app.middleware("http")
# async def add_process_time_handler(request: Request, call_next):
#     start_time = time.time()
#     # call_next 处理了所有的错误，这里不会抛出错误，所以也就捕捉不到错误。
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     print(f"耗费时间：{process_time:0.6f} seconds")
#     # response.headers["X-Process-Time"] = str(process_time)
#     return response


# cors 配置,对app起作用，并非全局，子app也需要配置
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:1718",
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    # return {"msg": "Hello World"}
    return RedirectResponse(url="/udadmin/docs")
    # return RedirectResponse(url="/docs")


@app.get("/favicon.ico")
async def get_favicon():
    # return {"file": "static/favicon.ico"}
    return FileResponse("static/favicon.ico")


# 使用模板渲染器处理根路径
templates = Jinja2Templates(directory="static")


@app.get("/admin", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("/dist/index.html", {"request": request})


# 捕获所有其他路径并返回 index.html
@app.get("/admin/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    return templates.TemplateResponse("/dist/index.html", {"request": request})
