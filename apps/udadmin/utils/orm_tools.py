from typing import Optional, Union, List
from pydantic import PositiveInt, Field
from pydantic.main import create_model
from tortoise.expressions import Q
from math import ceil

from . import pmodels as pm
from . import enums as es  # import M2mAction, create_enum_class


def build_Q_filter(filters, model):
    valid_fields = model._meta.db_fields

    def build_q_from_filter(condition):
        c = condition
        if c["field"] not in valid_fields:
            raise Exception(
                f"filter field[{c['field']}] not in model[{model.__name__}]"
            )
        value = c["value"]
        symbol = c["symbol"]
        # TODO: json 字段暂时不支持icontains,contains
        if symbol in [
            "contains",
            "icontains",
            "startswith",
            "endswith",
            "lt",
            "lte",
            "gt",
            "gte",
            "in",
            "not_in",
            "not_in",
            "isnull",
            "range",
            "not",  # 不等于
        ]:
            return Q(**{f"{c['field']}__{symbol}": value})
        elif symbol == "eq":
            return Q(**{f"{c['field']}": value})
        else:
            raise Exception(f"symbol error:[{symbol}] not configured.")

    def process_filter_group(filter_group):
        if isinstance(filter_group, list):
            # 处理嵌套的过滤条件组
            if len(filter_group) == 0:
                return Q()
            elif len(filter_group) == 1:
                return process_filter_group(filter_group[0])
            else:
                # 第一个元素是逻辑操作符
                logic = filter_group[0]
                if logic not in ["and", "or"]:
                    raise Exception(f"Invalid logic operator: {logic}")

                # 处理剩余的条件
                q = process_filter_group(filter_group[1])
                for condition in filter_group[2:]:
                    next_q = process_filter_group(condition)
                    if logic == "and":
                        q = q & next_q
                    else:  # or
                        q = q | next_q
                return q
        else:
            # 处理单个过滤条件
            return build_q_from_filter(filter_group)

    # 如果没有条件，返回空的Q对象
    if not filters:
        return Q()

    # 处理过滤条件
    return process_filter_group(filters)


# 这里会有两种情况，一种是model模型分页（默认），还是对象本身的关系字段分页（就要传入模型关系，以及关系对应的模型）
async def get_model_objs(pb: pm.PaginatorBody, model, fields=["*"], label=False):
    page_obj = model
    qs = build_Q_filter(pb.filters, model)
    total = await page_obj.filter(qs).count()
    if total == 0:
        return [], 0, 0
    page_cnt = ceil(total / pb.page_size)
    if pb.curr_page > page_cnt:
        raise Exception(
            f"page out of range.current_page:{pb.curr_page} > total_page_cnt:{page_cnt}"
        )
    page_objs = (
        page_obj.filter(qs)
        .order_by(*pb.order_by)
        .offset((pb.curr_page - 1) * pb.page_size)
        .limit(pb.page_size)
    )
    if "*" in fields:
        objs = await page_objs.values()
    else:
        objs = await page_objs.values(*fields)
    if label:
        data = [{"label": k, "value": v} for k, v in zip([str(i) for i in await page_objs], objs)]
    else:
        data=objs
    return data, total, page_cnt


async def get_relation_objs(
    pb: pm.PaginatorBody, related_model, fields=["*"], related_objs=None, label=False
):
    qs = build_Q_filter(pb.filters, related_model)
    total = await related_objs.filter(qs).count()
    if total == 0:
        return [], 0, 0
    page_cnt = ceil(total / pb.page_size)
    if pb.curr_page > page_cnt:
        raise Exception(
            f"page out of range.current_page:{pb.curr_page} > total_page_cnt:{page_cnt}"
        )
    page_objs = (
        related_objs.filter(qs)
        .order_by(*pb.order_by)
        .offset((pb.curr_page - 1) * pb.page_size)
        .limit(pb.page_size)
    )
    if "*" in fields:
        objs = await page_objs.values()
    else:
        objs = await page_objs.values(*fields)
    if label:
        if isinstance(objs, list):
            data = [{"label": k, "value": v} for k, v in zip([str(i) for i in await page_objs], objs)]
        elif  isinstance(objs, dict):
            data = [{"label": str(await page_objs), "value": objs}]
        else:
            raise Exception(f"objs type error:[{type(objs)}]")
    else:
        if isinstance(objs, list):
            data = objs
        elif isinstance(objs, dict):
            data=[objs]
    return data, total, page_cnt


def get_body_class(model):
    fields = model._meta.fetch_fields
    class_prefix = (
        f"{(model._meta.app or '').capitalize()}{model.__name__.capitalize()}"
    )
    enum_dict = {i: i for i in fields}
    f_enum_cls_name = f"{class_prefix}M2mFieldEnum"
    f_manage_cls_name = f"{class_prefix}M2mManage"
    DynamicEnum = es.create_enum_class(f_enum_cls_name, enum_dict)
    DynamicEnum.__doc__ = f"values for 'field_name' in {f_manage_cls_name}"
    M2mManageBody = create_model(
        f_manage_cls_name,
        action=(es.M2mAction, Field(description=f"One of {es.M2mAction.values()}")),
        label=(bool, False),
        field_name=(
            DynamicEnum,
            Field(
                description=f"One of {DynamicEnum.__name__}:{[i.value for i in DynamicEnum]}"
            ),
        ),
        # id=(Union[PositiveInt, int], None),
        id=(PositiveInt, None),
        paginator=(Optional[pm.PaginatorBody], None),
        m2m_ids=(dict, {"add": [],"del": []}),
    )
    M2mManageBody.__doc__ = f"fetch fields manage for {model.__name__}"

    return M2mManageBody
