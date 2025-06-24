from copy import deepcopy
from fastapi import FastAPI, APIRouter, Depends, Path
from fastapi.encoders import jsonable_encoder

# from starlette import status
from tortoise import fields, Tortoise
from tortoise.models import Model
from tortoise.expressions import Q
from tortoise.contrib.pydantic import pydantic_model_creator
from collections import OrderedDict

from typing import Annotated
from dateutil import parser
from math import ceil

# from typing import Optional, Union, List

# from datetime import timedelta

# from starlette.requests import Request
# from pydantic import PositiveInt, Field
# from pydantic.main import create_model

import re

from .decorator import timer
from .class_tools import SingletonMeta
from . import orm_tools as ot
from . import resp_code as rc
from . import auth
from . import enums as es  # import M2mAction, create_enum_class
from . import pmodels as pm
from . import ui_tools
from . import doc
from . import udtools as ut
from .. import models as md
from .model_perms import perms
from ..types import http_resp as hr

# from apps.udadmin.utils.objdoc import get_structure
from config import settings

# models to pydantic
# UserPydantic = pydantic_model_creator(User)
# from tortoise.contrib.pydantic import pydantic_model_creator
app_models = Tortoise.apps


class ModleRegister(metaclass=SingletonMeta):
    name: str = "ModleTools"
    models_info: dict = {}
    routes: dict = {}  # 记录route 是否添加了get_model_info方法
    registered_info = set()
    perm_type = "model"  # 模型的增删改查的权限类型名称

    # _models_config = None

    # def get_model_info(self, model, ui_info: ui_info.UiInfo):
    def get_model_info(self, model):
        app_name = model._meta.app
        model_name = model.__name__.lower()
        model_fields = model._meta.fields_map
        # 字段按照模型定义顺序排序
        if order := getattr(model, "_order_fields"):
            sorted_dict = OrderedDict(
                (key, model_fields[key]) for key in order if key in model_fields
            )
            sorted_dict.update(
                (key, model_fields[key])
                for key in model_fields
                if key not in sorted_dict
            )
            model_fields = sorted_dict
        api_docs = {}
        fields_doc = []
        fileds_info = {}
        datetime_fields = []
        pk = model._meta.pk_attr
        for field_name, field in model_fields.items():
            # 处理字段
            # 属性值
            ud_name = getattr(field, "ud_name", field_name)
            # ui_desc = field.description
            ui_desc = getattr(field, "description", "")
            field_type = field.__class__.__name__
            sql_type = field.SQL_TYPE
            default = f"_default:{field.default}_" if field.default else ""

            # 布尔
            is_required = field.required
            is_read_only = field.constraints.get("readOnly") or False
            is_fk = (
                True
                if isinstance(field, fields.relational.ForeignKeyFieldInstance)
                else False
            )
            is_m2m = (
                True
                if isinstance(field, fields.relational.ManyToManyFieldInstance)
                else False
            )
            is_o2o = (
                True
                if isinstance(field, fields.relational.OneToOneFieldInstance)
                else False
            )
            has_db_field = field.has_db_field

            # 标识
            pk_tag = ut.font("#", color="#ff0000") if field.pk else "#"
            required_tag = (
                ut.font("\\*", color="#ff0000") if is_required else ut.font("\\*")
            )
            read_only_tag = (
                ut.font("❶", color="#ff0000") if is_read_only else ut.font("❶")
            )
            db_field_tag = (
                ut.font("❷", color="#ff0000") if has_db_field else ut.font("❷")
            )
            # 可选值
            choices = ""
            if enums := getattr(field, "enum_type", None):
                choices = f"_可选值:{[item.value for item in enums]}_"

            if isinstance(field, fields.data.DatetimeField):
                datetime_fields.append(field_name)

            fields_doc.append(
                (
                    f"- [{pk_tag}{required_tag}{read_only_tag}{db_field_tag}]"
                    f"__{field_name}({ud_name or 'None'})__ "
                    f"_&lt;{field_type}({sql_type})&gt;_ __:__ "
                    # f"{f"__{ui_desc}__" if ui_desc else ""} "
                    f"{ui_desc} "
                    f"{default} {choices}"
                )
            )
            fileds_info[field_name] = {
                "app_name": app_name,
                "model_name": model_name,
                "field_name": field_name,
                "ud_name": ud_name,
                "ud_order": getattr(field, "ud_order", None),
                "description": ui_desc,
                "is_required": is_required,
                "default": field.default,
                "choices": [item.value for item in enums] if enums else None,
                "has_db_field": has_db_field,
                "is_pk": field.pk,
                "is_fk": is_fk,
                "is_m2m": is_m2m,
                "is_o2o": is_o2o,
                "generated": field.generated,
                "unique": field.unique,
                "null": field.null,
                "index": field.index,
                "indexable": field.indexable,
                "read_only": is_read_only,
                "field_type": field_type,
                "decimal_places": getattr(field, "decimal_places", None),
                "max_digits": getattr(field, "max_digits", None),
                "source_field": field.source_field,
                # "related_model":field.related_model.__name__
                # "related_model": (
                #     field.related_model.__name__
                #     if getattr(field, "related_model", None)
                #     else None
                # ),
            }

        fields_doc = "\n".join(fields_doc)

        api_docs["create_item"] = doc.create_item.format(
            app_name=app_name,
            model_name=model_name,
            perm="create",
            fields=fields_doc,
        )
        api_docs["delete_item"] = doc.delete_item.format(
            app_name=app_name,
            model_name=model_name,
            pk=pk,
            perm="delete",
        )
        api_docs["update_item"] = doc.update_item.format(
            app_name=app_name,
            model_name=model_name,
            perm="update",
            fields=fields_doc,
        )
        api_docs["read_item"] = doc.read_item.format(
            app_name=app_name,
            model_name=model_name,
            pk=pk,
            perm="read",
            fields=fields_doc,
        )
        api_docs["get_item_list"] = doc.get_item_list.format(
            app_name=app_name,
            model_name=model_name,
            perm="list",
            fields=fields_doc,
        )
        api_docs["fetch_manage"] = doc.fetch_manage.format(
            app_name=app_name,
            model_name=model_name,
            perm="fetch",
            fetch_action=es.M2mAction.values(),
            fetch_fields=model._meta.fetch_fields,
        )
        model_info = {
            # "ui": ui_info,
            "model": model,
            "menu_name": getattr(model.Meta, "menu_name", model_name),
            "fileds_info": fileds_info,
            "app": app_name,
            "tb_name": getattr(model.Meta, "table", model_name),
            "tb_description": getattr(model.Meta, "table_description", model_name),
            "model_name": model_name,
            "fields_doc": fields_doc,
            "api_docs": api_docs,
            "datetime_fields": datetime_fields,
        }
        return model_info

    def create_item_generator(self, model, info):
        pmodel = pydantic_model_creator(
            model,
            name=f"In{model.__name__}",
            # exclude=model._meta.fetch_fields,
            exclude_readonly=True,
        )

        @auth.permission_required(
            f"model", f"{info['app']}:{info['model_name']}:{perms['create']}"
        )
        async def create_item(
            user: Annotated[str, Depends(auth.get_user)],
            item: pmodel,  # type: ignore
        ):
            # 检查是否含有只读字段
            rd = info["ui"].check_readonly(item.dict())
            if rd:
                raise Exception(f"readonly field cannot be set:{rd}")
            # 字段值入库前处理
            for k, v in info["ui"].db_value_converters.items():
                setattr(item, k, v(getattr(item, k)))
            obj = await model.create(**item.model_dump(exclude_unset=True))
            return {
                "code": rc.success,
                "data": obj,
                "msg": "ok",
            }

        # create_item.__annotations__ = {"item": pmodel}

        return create_item

    def delete_item_generator(self, model, info):
        @auth.permission_required(
            f"model", f"{info['app']}:{info['model_name']}:{perms['delete']}"
        )
        async def delete_item(
            user: Annotated[str, Depends(auth.get_user)],
            id: int = Path(title="The ID of the item"),
        ):
            item_filter = {model._meta.pk_attr: id}
            ret = await model.filter(**item_filter).delete()
            # 实例存在ret就是1，不存在就是0
            return {"code": rc.success, "msg": "ok", "data": ret}

        return delete_item

    def update_item_generator(self, model, info):
        @auth.permission_required(
            f"model", f"{info['app']}:{info['model_name']}:{perms['update']}"
        )
        async def update_item(
            user: Annotated[str, Depends(auth.get_user)],
            item: dict,
            id: int = Path(title="The ID of the item"),
        ):
            # 检查是否是只读字段
            rd = info["ui"].check_readonly(item)
            if rd:
                raise Exception(f"readonly field cannot be set:{rd}")

            # 日期字段处理
            if dt_fields := info.get("datetime_fields", None):
                for field in dt_fields:
                    if field in item:
                        item[field] = parser.parse(item[field])
            # 字段值入库前处理
            for k, v in info["ui"].db_value_converters.items():
                if k in item:
                    item[k] = v(item[k])
            item_filter = {model._meta.pk_attr: id}
            ret = await model.filter(**item_filter).update(**item)
            if ret == 1:
                return {"code": rc.success, "msg": "ok", "data": ret}
            else:
                return {
                    "code": rc.success_request,
                    "msg": "success request but not change the info,The database has no action,please check object-id or update-fields",
                    "data": ret,
                }

        # update_item.__annotations__ = {"item": pmodel}
        return update_item

    def read_item_generator(self, model, info):
        @auth.permission_required(f"model", f"{info['app']}:{info['model_name']}:{perms['read']}")
        async def get_item(
            user: Annotated[str, Depends(auth.get_user)],
            id: int = Path(title="The ID of the item"),
        ):
            item_filter = {model._meta.pk_attr: id}
            obj = await model.get_or_none(**item_filter)
            if not obj:
                raise Exception(f"model:<{model.__name__}> [id={id}] is not in db.")
            obj = jsonable_encoder(obj)
            list_display = info.get("ui").list_display
            if "*" not in list_display:
                obj = {k: v for k, v in obj.items() if k in list_display}
            return {
                "code": rc.success,
                "data": obj,
                "msg": "ok",
            }

        return get_item

    def get_item_list_generator(self, model, info):
        @auth.permission_required(f"model", f"{info['app']}:{info['model_name']}:{perms['list']}")
        async def get_item_list(
            user: Annotated[str, Depends(auth.get_user)],
            pb: pm.PaginatorBody,
        ):
            objs, total, page_cnt = await ot.get_model_objs(
                pb, model, fields=info.get("ui").list_display
            )
            return {
                "code": rc.success,
                "data": objs,
                "msg": "ok",
                "extra": {
                    "paginator": {
                        "curr_page": pb.curr_page,
                        "page_size": pb.page_size,
                        "total": total,
                        "page_cnt": page_cnt,
                    }
                },
            }

        return get_item_list

    def relation_manage_generator(self, model, info):
        req_class = ot.get_body_class(model)

        @auth.permission_required(f"model", f"{info['app']}:{info['model_name']}:{perms['read']}")
        async def fetch_manage(
            user: Annotated[str, Depends(auth.get_user)],
            reqb: req_class,  # type: ignore
        ):
            action = reqb.action.value
            id = reqb.id
            paginator = reqb.paginator
            field_name = reqb.field_name.value
            m2m_ids = reqb.m2m_ids or {"add": [], "del": []}
            label = reqb.label

            assert (
                # field_name in model._meta.fetch_fields
                field_name
                in model._meta.fetch_fields
            ), f"field_name:<{field_name}> is not in fetch_fields."
            m_field = model._meta.fields_map[field_name]
            related_model = m_field.related_model
            if id:
                obj = await model.filter(id=id).first()
                if not obj:
                    raise Exception(f"model:<{model.__name__}> [id={id}] is not found.")
                # 这里如果传入的field_name是外键，那么related_objs就只有一个对象，如果是多对多，那么related_objs就是个列表
                related_objs = getattr(obj, field_name)
            # 对象身上的关系管理，需要传入对象id，
            if action == "list":
                assert id, "id cannot be null or '' when action is 'list'"
                assert paginator, "paginator cannot be null when action is 'list'"
                objs, total, page_cnt = await ot.get_relation_objs(
                    paginator,
                    related_model,
                    fields=["*"],
                    related_objs=related_objs,
                    label=label,
                )
                return {
                    "code": rc.success,
                    "data": objs,
                    "msg": "ok",
                    "extra": {
                        "paginator": {
                            "curr_page": paginator.curr_page,
                            "page_size": paginator.page_size,
                            "total": total,
                            "page_cnt": page_cnt,
                        },
                        "related_model": related_model.__name__.lower(),
                        "app_name": related_model._meta.app,
                    },
                }
            elif action == "manage":
                assert id, "id cannot be null when action is 'manage'"
                assert m2m_ids, "m2m_ids cannot be null when action is 'manage'"
                add_ids, del_ids = [], []
                if m2m_ids.get("add"):
                    add_objs = await related_model.filter(id__in=m2m_ids["add"])
                    add_ids = await related_objs.add(*add_objs)
                if m2m_ids.get("del"):
                    del_objs = await related_model.filter(id__in=m2m_ids["del"])
                    del_ids = await related_objs.remove(*del_objs)
                return {
                    "code": rc.success,
                    "msg": "manage done!",
                }
            # 对象关联的关系模型查询 可以不需要对象本身，只需要关联模型
            elif action == "query":
                assert paginator, "paginator cannot be null when action is 'query'"
                objs, total, page_cnt = await ot.get_model_objs(
                    paginator,
                    related_model,
                    fields=["*"],
                    label=label,
                )
                return {
                    "code": rc.success,
                    "data": objs,
                    "msg": "ok",
                    "extra": {
                        "paginator": {
                            "curr_page": paginator.curr_page,
                            "page_size": paginator.page_size,
                            "total": total,
                            "page_cnt": page_cnt,
                        }
                    },
                }
            else:
                raise Exception(f"action:<{action}> is not supported.")

        return fetch_manage

    def get_all_models_info_generator(self):

        async def get_all_models_info(
            user: Annotated[str, Depends(auth.get_user)],
        ):
            # user = await md.User.filter(id=2).first()
            allow_models = await self.get_allow_models(user)
            all_models = {}
            app_info = settings.APP_INFO
            for app_name, models in app_models.items():
                for model_name, model in models.items():
                    union_name = f"{app_name}:{model_name.lower()}"
                    Meta = model.Meta
                    ud_app = getattr(Meta, "ud_app", None) or app_name
                    icon = getattr(Meta, "icon", None)
                    if union_name in allow_models:
                        all_models[union_name] = {
                                "model_menu_name": getattr(Meta, "menu_name", model_name),
                                "app": app_name,
                                "ud_app": ud_app,
                                "tb_name": getattr(Meta, "table", model_name.lower()),
                                "tb_description": getattr(
                                    Meta, "menu_name", model_name
                                ),
                                "model_icon": icon,
                                "model_name": model_name.lower(),
                                **app_info.get(ud_app, {})
                        }
            return {
                "code": rc.success,
                "data": {
                    "all_models": all_models,
                    # "allow_models": allow_models,
                    # "allow_models_info": allow_models_info,
                },
                "msg": "ok",
            }
        return get_all_models_info

    def get_allow_model_info_generator(self):
        async def get_allow_model_info(
            user: Annotated[str, Depends(auth.get_user)],
            req: pm.AllowModel,
        ):
            # user = await md.User.filter(id=2).first()
            # 获取请求中的app_name和model_name，拼接成union_name
            union_name = req.model_name
            # 获取用户对union_name的权限
            perms = await self.get_user_model_perms(user, union_name)
            perms = [v.name for v in perms]
            # 检查union_name是否已经注册
            await self.check_model_register(union_name)
            # 检查用户是否有权限使用union_name
            await self.check_model_allow(user, union_name)
            # 定义需要返回的字段
            keys = ["ui", "fileds_info"]
            # 从models_info中获取需要的字段
            allow_info = {
                k: v for k, v in self.models_info[union_name].items() if k in keys
            }
            # 对fileds_info按ud_order排序
            # allow_info["fileds_info"].sort(key=lambda x: x["ud_order"])
            # 返回结果
            return {
                "code": rc.success,
                "data": {
                    "allow_model": union_name,
                    "fields_info": allow_info["fileds_info"],
                    "ui": allow_info["ui"],
                    "perms": perms,
                },
                "msg": "ok",
            }

        return get_allow_model_info

    def get_filter_fields_distinct_values_generator(self):
        async def get_filter_fields_distinct_values(
            user: Annotated[str, Depends(auth.get_user)],
            req: pm.FilterFieldsDistinctValues,
        ):
            # user = await md.User.filter(id=2).first()
            union_name = req.app_model_name
            # 检查权限
            await self.check_model_register(union_name)
            await self.check_model_allow(user, union_name)

            if union_name not in self.models_info:
                raise Exception(f"model:<{union_name}> is not registered.")
            model_info = self.models_info[union_name]
            model = model_info["model"]
            ui_info = model_info["ui"]
            if req.field_names not in ui_info.list_filter:
                raise Exception(
                    f"field_name:<{req.field_names}> is not in models`s list_filter."
                )
            pb = req.paginator
            qs = ot.build_Q_filter(pb.filters, model)
            field = req.field_names

            total_query = (
                model.filter(qs)
                .distinct()
                .order_by(field)
                # .offset((pb.curr_page - 1) * pb.page_size)
                # .limit(pb.page_size)
                .values(field)
            )
            # 这个是先获取所有数据再求len，性能不好
            # total = len(await total_query)
            # 以下是优化后的代码,直接执行查询计算值的个数
            sql = f"SELECT count(*) AS cnt FROM ({total_query.sql(params_inline=True)}) virtual_table"
            affected_rows, rows_list = await model._meta.db.execute_query(sql)
            total = rows_list[0]["cnt"]
            page_query = (
                model.filter(qs)
                .distinct()
                .order_by(field)
                .offset((pb.curr_page - 1) * pb.page_size)
                .limit(pb.page_size)
                .values(field)
            )

            distinct_values_dict = await page_query
            if total == 0:
                return {
                    "code": rc.success_request,
                    "data": {"values": [], "paginator": pb},
                    "msg": f"no data with filter:{pb.filters}",
                }
            page_cnt = ceil(total / pb.page_size)
            if pb.curr_page > page_cnt:
                raise Exception(
                    f"page out of range.current_page:{pb.curr_page} > page_cnt:{page_cnt}"
                )
            distinct_values = [i[field] for i in distinct_values_dict]
            data = {
                "values": distinct_values,
                "paginator": {
                    "curr_page": pb.curr_page,
                    "page_size": pb.page_size,
                    "total": total,
                    "page_cnt": page_cnt,
                },
            }
            return {
                "code": rc.success,
                "data": data,
                "msg": "ok",
            }

        return get_filter_fields_distinct_values

    async def get_allow_models(self, user: md.User):
        if user.is_superuser:
            perms = list(self.models_info.keys())
        else:
            user_perms = await md.Permission.filter(
                Q(permission_type__name=self.perm_type) & Q(users__id=user.id)
            ).values("name")
            user_perms = [perm["name"] for perm in user_perms]
            role_perms = await md.Permission.filter(
                Q(permission_type__name=self.perm_type) & Q(roles__users__id=user.id)
            ).values("name")
            role_perms = [perm["name"] for perm in role_perms]
            perms = list(set(user_perms) | set(role_perms))
        return {
            match.group(0)
            for perm in perms
            if (match := re.search(r"([^:]+:[^:]+)", perm))
        }

    async def get_user_model_perms(self, user: md.User, union_name: str):
        if user.is_superuser:
            perms = await md.Permission.filter(
                Q(permission_type__name=self.perm_type)
                & Q(name__istartswith=union_name)
            )
        else:
            user_perms = await md.Permission.filter(
                Q(permission_type__name=self.perm_type)
                & Q(users__id=user.id)
                & Q(name__istartswith=union_name)
            )
            role_perms = await md.Permission.filter(
                Q(permission_type__name=self.perm_type)
                & Q(roles__users__id=user.id)
                & Q(name__istartswith=union_name)
            )
            perms = list(set(user_perms) | set(role_perms))
        return perms

    async def check_model_register(self, union_name: str):
        if union_name not in list(self.models_info.keys()):
            raise Exception(
                {
                    "code": 5010,
                    "error": f"Please confirm if model '{union_name}' is registered?",
                }
            )

    async def check_model_allow(self, user: md.User, union_name: str):
        allow_models = await self.get_allow_models(user)
        if union_name not in allow_models:
            raise Exception(
                {
                    "code": 5010,
                    "error": f"user:{user.username} have not permission to access this model[{union_name}].",
                }
            )
        return allow_models

    # @timer
    def register(
        self,
        router: FastAPI | APIRouter,
        model: Model,
        doc_tags: list[str] = ["Registered Model Api"],
        crudl: str = "crudl",
        fetch: bool = True,
        prefix: str = "models",
        # db_value_converters: dict = {},
        ui_info: ui_tools.UiInfo = ui_tools.UiInfo(),
    ):
        app_name = model._meta.app
        model_name = model.__name__.lower()
        union_key = f"{app_name}:{model_name}"
        # ui_info = ui.UiInfo(**self._models_config.get(union_key, {}))

        router_id = id(router)
        model_id = id(model)
        # 获取该路由所有注册的模型信息的接口,如果router 已经注册过这个路由了就不需要再次注册了
        info_tag = ["Models Info Api"]
        if router_id not in self.routes.keys():
            router.add_api_route(
                f"/get_all_models_info",
                self.get_all_models_info_generator(),
                methods=["get"],
                tags=info_tag,
                responses=hr.general_resps,
                description="获取所有已经注册的有权限的模型的信息。",
            )
            router.add_api_route(
                f"/get_allow_model_info",
                self.get_allow_model_info_generator(),
                methods=["post"],
                tags=info_tag,
                responses=hr.general_resps,
                description="获取所有已经注册的模型的信息。",
            )
            router.add_api_route(
                f"/get_filter_fields_distinct_values",
                self.get_filter_fields_distinct_values_generator(),
                methods=["post"],
                tags=info_tag,
                responses=hr.general_resps,
                description=doc.field_distinct.format(model_name=model_name),
            )
            # 记录router已经注册信息路由
            self.routes[router_id] = router

        register_id = f"{router_id}#{model_id}"
        if register_id in self.registered_info:
            raise Exception(
                f"model:<{model_name}> is already registered in router:<{router}>."
            )
        else:
            self.registered_info.add(register_id)

        snake_model_name = ut.camel_to_snake_case(model_name)
        if union_key in self.models_info.keys():
            model_info = self.models_info.get(union_key)
        else:
            # model_info = self.get_model_info(model, ui_info)
            model_info = self.get_model_info(model)
            model_info["ui"] = ui_info
            model_info["url"] = f"{prefix}/{snake_model_name}"
            # model_info["db_value_converters"] = db_value_converters
            self.models_info[f"{app_name}:{model_name}"] = model_info
        # 创建路由
        # 增记录
        prefix = (prefix if prefix.startswith("/") else f"/{prefix}") if prefix else ""
        if "c" in crudl:
            router.add_api_route(
                f"{prefix}/{snake_model_name}",
                self.create_item_generator(model, model_info),
                methods=["post"],
                tags=doc_tags,
                responses=hr.general_resps,
                description=model_info["api_docs"]["create_item"],
            )

        # 删记录
        if "d" in crudl:
            router.add_api_route(
                f"{prefix}/{snake_model_name}/{{{model._meta.pk_attr}}}",
                self.delete_item_generator(model, model_info),
                methods=["delete"],
                tags=doc_tags,
                responses=hr.general_resps,
                description=model_info["api_docs"]["delete_item"],
            )

        # 改记录
        if "u" in crudl:
            router.add_api_route(
                f"{prefix}/{snake_model_name}/{{{model._meta.pk_attr}}}",
                self.update_item_generator(model, model_info),
                methods=["put"],
                tags=doc_tags,
                responses=hr.general_resps,
                description=model_info["api_docs"]["update_item"],
            )

        # 查记录
        if "r" in crudl:
            router.add_api_route(
                f"{prefix}/{snake_model_name}/{{{model._meta.pk_attr}}}",
                self.read_item_generator(model, model_info),
                methods=["get"],
                tags=doc_tags,
                responses=hr.general_resps,
                description=model_info["api_docs"]["read_item"],
            )

        # 查列表
        if "l" in crudl:
            router.add_api_route(
                f"{prefix}/{snake_model_name}/list",
                self.get_item_list_generator(model, model_info),
                methods=["post"],
                tags=doc_tags,
                responses=hr.general_resps,
                description=model_info["api_docs"]["get_item_list"],
            )

        # 多对多关系操作
        if fetch and model._meta.fetch_fields:
            router.add_api_route(
                f"{prefix}/{snake_model_name}/fetch_manage",
                self.relation_manage_generator(model, model_info),
                methods=["post"],
                tags=doc_tags,
                responses=hr.general_resps,
                description=model_info["api_docs"]["fetch_manage"],
            )


mr = ModleRegister()

if __name__ == "__main__":
    pass
