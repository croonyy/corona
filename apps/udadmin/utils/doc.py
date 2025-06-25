from . import udtools as ut

tips = (
    "<br>Tips:  \n"
    f"  1. {ut.font('#',color='#ff0000')}(primary_key), "
    f"{ut.font('*',color='#ff0000')}(required),"
    f"{ut.font('❶',color='#ff0000')}(read_olny),"
    f"{ut.font('❷',color='#ff0000')}(has_db_field),  \n"
    "  2. [{{pk_tag}}{{required_tag}}{{read_only_tag}}{{db_field_tag}}]"
    "{{__field_name__}}({{__ud_name__}}) "
    "_&lt;{{field_type}}({{sql_type}})&gt;_ __:__ "
    "{{ui_desc}} "
    "{{default}} {{choices}}"
)


paginator_doc = (
    "- __curr_page__: current page number\n"
    "- __page_size__: size per page\n"
    '- __order_by__: ["field1","-fileld2",...] "field1" for asc,"-field2" for desc,...\n'
    '- __filters__: ["or", ["and", {{"field": "username", "symbol": "icontains", "value": "user"}}, {{"field": "gender", "symbol": "eq", "value": "女"}}], ["and", {{"field": "username", "symbol": "icontains", "value": "user"}}, {{"field": "username", "symbol": "eq", "value": "aa"}}]]  '
    """<br>Tips:  \n  """
    f"""1. {ut.font("symbol",color='#ff0000')}: __contains__|__icontains__(ignore case)|__startswith__|__endswith__|__lt__(less then)|__lte__(less then or equal)|__gt__(great then)|__gte__(great then or equal)|__in__|__not_in__|__not_in__|__isnull__|__range__|__not__(not equal)|__eq__(equal)  \n"""
    f"""  2. {ut.font("value",color='#ff0000')}: "Jack"|[1, 2, 3,...]|["a", "b", "c",...]\n"""
)

create_item = (
    "## Function:  \n"
    "Pass in the following valid key value pairs to create a &lt;__{model_name}__&gt; object.  \n"
    "## Need permission:  \n"
    "perm_type [__model__], perm_name [__{app_name}:{model_name}:{perm}__]  \n"
    "## Field Description:  \n"
    "{fields}  "
    f"{tips}  \n"
)


delete_item = (
    "## Function:  \n"
    "Delete &lt;__{model_name}__&gt; object based on the value of the primary key __{pk}__.  \n"
    "## Need permission:  \n"
    "perm_type [__model__], perm_name [__{app_name}:{model_name}:{perm}__]  \n"
)


update_item = (
    "## Function:  \n"
    "Pass in a key value pair object containing the valid fields in "
    "[Field Description] and update a &lt;__{model_name}__&gt;object.  \n"
    "## Need permission:  \n"
    "perm_type [__model__], perm_name [__{app_name}:{model_name}:{perm}__]  \n"
    "## Field Description:  \n"
    "{fields}  "
    f"{tips}  \n"
)

read_item = (
    "## Function:  \n"
    "Get &lt;__{model_name}__&gt; object based on the value of the primary key __{pk}__.  \n"
    "## Need permission:  \n"
    "perm_type [__model__], perm_name [__{app_name}:{model_name}:{perm}__]  \n"
    "## Field Description:  \n"
    "{fields}  "
    f"{tips}  \n"
)


get_item_list = (
    "## Function:  \n"
    "Get &lt;__{model_name}__&gt; list.  \n  "
    "## Need permission:  \n"
    "perm_type [__model__], perm_name [__{app_name}:{model_name}:{perm}__]  \n"
    "## Field Description:  \n"
    "{fields}  "
    f"{tips}  \n"
    "## Request Body Description: \n"
    f"{paginator_doc}"
)


fetch_manage = (
    "## Function:  \n  Manage relation fields of &lt;__{model_name}__&gt;.  \n  "
    "## Need permission:  \n"
    "perm_type [__model__], perm_name [__{app_name}:{model_name}:{perm}__]  \n"
    "## Request Body Description: \n"
    "- __action__: one of {fetch_action}.\n"
    "- __field_name__: one of {fetch_fields}.\n"
    "- __id__: id of &lt;__{model_name}__&gt; object.\n"
    f"{paginator_doc}"
    "- __m2m_ids__: The relative-objects'ids to be add/delete in relations of item.\n"
)

field_distinct = (
    "## Function:  \n  Get paged distinct-value list of fields of modle &lt;__{model_name}__&gt;.  \n  "
    "## Request Body Description: \n"
    f"{paginator_doc}"
)
