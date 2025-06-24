from tortoise.models import Model


class UiInfo:

    def __init__(
        self,
        model: Model = None,
        list_display=["*"],
        list_per_page=10,
        list_filter=[],
        search_fields=[],
        readonly_fields=[],
        db_value_converters={},
        relation_search={},
        **kwargs,
    ):
        self.list_display = list_display
        self.list_per_page = list_per_page
        self.list_filter = list_filter
        self.search_fields = search_fields
        self.readonly_fields = readonly_fields
        self.db_value_converters = db_value_converters
        self.relation_search = relation_search
        for k, v in kwargs.items():
            setattr(self, k, v)
        if model:
            self._check(model)

    def check_readonly(self, item) -> list[str]:
        return [i for i in item.keys() if i in self.readonly_fields]

    def _check(self, model):
        fields = model._meta.fields | {"*"} # 合并两个set，产生一个新set
        attrs = ["list_display", "list_filter", "search_fields", "readonly_fields"]
        for attr in attrs:
            attr_v = getattr(self, attr)
            if tmp := [i for i in attr_v if i not in fields]:
                raise ValueError(
                    f"UiInfo {attr} config error:{tmp} not in model fields"
                )
        if tmp := [i for i in self.db_value_converters.keys() if i not in fields]:
            raise ValueError(
                f"UiInfo db_value_converters config error:{tmp} not in fields of model[{model._meta.app}:{model.__name__}] "
            )


if __name__ == "__main__":
    a = UiInfo(test="aa")
    print(getattr(a, "test1", None))
    print(getattr(a, "test", None))
