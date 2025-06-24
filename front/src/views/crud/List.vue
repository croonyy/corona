<template>
  <div>
    <n-card v-if="conditionCardVisible" :bordered="false" class="condition-card">
      <BasicForm @register="register" @submit="handleSubmit" @reset="handleReset">
        <template #statusSlot="{ model, field }">
          <n-input v-model:value="model[field]" />
        </template>
      </BasicForm>
    </n-card>

    <!-- <TextOutline /> -->

    <n-card :bordered="false" class="mt-3">
      <!-- v-if="pk" -->
      <!-- title="表格列表" 被插槽覆盖了-->
      <!-- :request="loadDataTable" -->
      <BasicTable
        v-if="pk"
        :columns="columns"
        :request="loadDataTable"
        :row-key="(row: Recordable[string]) => row.id"
        ref="actionRef"
        :actionColumn="actionColumn"
        @update:checked-row-keys="onCheckedRow"
        :scroll-x="scroll_x"
        :striped="true"
      >
        <template #tableTitle>
          <!-- 判断‘${appName}:${modelName}:create’权限，有则显示新建按钮，没有则不显示’ -->
          <template
            v-if="perms.includes(`${appName}:${modelName}:create`) || userInfo.is_superuser"
          >
            <n-button type="primary" @click="handleCreate">
              <template #icon>
                <n-icon>
                  <PlusOutlined />
                </n-icon>
              </template>
              新建
            </n-button>
          </template>
        </template>
      </BasicTable>
    </n-card>
  </div>
</template>

<script setup lang="ts">
  import {
    ref,
    computed,
    onMounted,
    reactive,
    h,
    onActivated, // 当组件缓存的时候，激活组件触发的钩子函数
    onDeactivated,
    onUnmounted, // 当组件缓存的时候，离开组件触发的钩子函数
    // nextTick,
    // watch,
  } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { BasicTable, TableAction } from '@/components/Table';
  import { BasicForm, FormSchema, useForm } from '@/components/Form/index';
  import { PlusOutlined } from '@vicons/antd';
  import { GetAllowModelInfo, DeleteModelItem, GetModelItemList } from '@/api/crud/models';
  import { FilterFieldComponentMap, GenerateFilter } from './compsFilter';
  import { SearchFieldComponent } from './compsSearch';
  import { columnRenderMap } from './columnRender';
  import { CRUD_LIST, CRUD_EDIT, CRUD_CREATE } from '@/store/consts';
  import { useCrudRefresh } from '@/store/modules/crudListRefresh';
  import { UserInfoType, useUserStore } from '@/store/modules/user';

  const userStore = useUserStore();
  const userInfo: UserInfoType = userStore.getUserInfo || {};

  const currentRoute = useRoute();
  const router = useRouter();
  // const route = useRoute();
  const crudRefresh = useCrudRefresh();
  const appName = computed(() => currentRoute.params.app_name as string);
  const modelName = computed(() => currentRoute.params.model_name as string);
  const modelInfo = ref();
  // const perms = modelInfo.value?.perms || [];
  const columns = ref<any[]>([]);
  const schemas = ref<FormSchema[]>([]);
  const actionRef = ref();
  const g_filters = ref<any[]>([]);
  const scroll_x = computed(() => columns.value.length * 150);
  const conditionCardVisible = computed<boolean>(() => {
    if (!modelInfo.value?.ui) return false;
    return modelInfo.value.ui.search_fields.length > 0 || modelInfo.value.ui.list_filter.length > 0;
  });
  const pk = ref<string>('');

  defineOptions({
    name: CRUD_LIST,
  });
  // 查询表单，getFieldsValue作用是获取表单的值
  const [register, { getFieldsValue }] = useForm({
    gridProps: { cols: '1 s:2 m:3 l:3 xl:4 2xl:5' },
    labelWidth: 80,
    // @ts-ignore
    // labelAlign: 'left',
    schemas,
  });

  // 查询表单提交
  async function handleSubmit(values: Recordable) {
    console.log('@@@getSearchFormValues', getFieldsValue());
    const filters = GenerateFilter(values, modelInfo);
    g_filters.value = filters;
    // 直接调用表格的reload方法刷新数据
    reloadTable();
  }
  // 表单重置
  function handleReset() {
    console.log('@@@handleReset');
  }

  const loadDataTable = async (res) => {
    // res 里面有查询的页码和每页条数
    const params = {
      curr_page: res.page || 1,
      page_size: res.pageSize || 20,
      order_by: [`-${pk.value}`],
      filters: g_filters.value,
    };
    const { data, extra } = await GetModelItemList(appName.value, modelName.value, params);
    const result = {
      itemCount: extra.paginator.total,
      list: data,
      page: extra.paginator.curr_page,
      pageCount: extra.paginator.page_cnt,
      pageSize: extra.paginator.page_size,
    };
    return result;
  };

  // 监听刷新标志变化
  // watch(
  //   () => crudRefresh.getRefreshFlag(appName.value, modelName.value),
  //   (needsRefresh) => {
  //     if (needsRefresh) {
  //       reloadTable();
  //       crudRefresh.clearRefreshFlag(appName.value, modelName.value);
  //     }
  //   }
  // );
  const perms = computed(() => {
    return modelInfo.value?.perms || [];
  });

  const actionColumn = reactive({
    width: 150,
    title: '操作',
    key: 'action',
    fixed: 'right',
    align: 'center',
    render(record) {
      const actions: any[] = [];
      if (
        perms.value.includes(`${appName.value}:${modelName.value}:delete`) ||
        userInfo.is_superuser
      ) {
        actions.push({
          label: '删除',
          onClick: handleDelete.bind(null, record),
          ifShow: () => true,
          type: 'error',
          size: 'tiny',
          // auth: ['basic_list'],
        });
      }
      if (
        perms.value.includes(`${appName.value}:${modelName.value}:update`) ||
        userInfo.is_superuser
      ) {
        actions.push({
          label: '编辑',
          onClick: handleEdit.bind(null, record),
          ifShow: () => true,
          type: 'warning',
          size: 'tiny',
          // auth: ['basic_list'],
        });
      }
      return h(TableAction as any, {
        style: 'button',
        actions,
      });
    },
  });

  // 新建记录
  async function handleCreate() {
    console.log(modelInfo.value?.perms.includes(`${appName.value}:${modelName.value}:create`));
    console.log('handleCreate');
    router.push({
      name: CRUD_CREATE,
      params: {
        app_name: appName.value,
        model_name: modelName.value,
      },
      // query: {
      //   is_edit: 'false',
      // },
    });
  }

  async function handleEdit(record) {
    console.log('handleEdit');
    router.push({
      name: CRUD_EDIT,
      params: {
        app_name: appName.value,
        model_name: modelName.value,
        id: record.id,
      },
      // query: {
      //   is_edit: 'true',
      // },
      replace: true,
    });
    return;
  }

  function onCheckedRow(rowKeys) {
    console.log(rowKeys);
  }

  function reloadTable() {
    console.log(`reloadTable:${appName.value},${modelName.value}`);
    actionRef.value?.reload();
  }

  async function handleDelete(record) {
    try {
      window['$dialog'].warning({
        title: '警告',
        content: '确定要删除该记录吗？',
        positiveText: '确定',
        negativeText: '取消',
        autoFocus: false,
        positiveButtonProps: {
          autofocus: true,
          udFocus: true,
          // type: 'primary',
          onclick: (e) => {
            console.log(e);
          },
        },
        onAfterEnter: () => {
          const btn = document.querySelector('button[udfocus="true"]') as HTMLElement;
          if (btn) {
            btn.focus();
          }
        },
        onPositiveClick: async () => {
          await DeleteModelItem(appName.value, modelName.value, record.id);
          window['$message'].success('删除成功');
          reloadTable();
        },
      });
    } catch (error: any) {
      window['$message'].error('删除失败: ' + error.message);
    }
  }

  onMounted(async () => {
    console.log(`@@@crud_list:${appName.value}:${modelName.value} onMounted`);
    const { data: model_info_data } = await GetAllowModelInfo({
      model_name: `${appName.value}:${modelName.value}`,
    });
    console.log('@@@model_info', model_info_data);
    modelInfo.value = model_info_data;
    const { fields_info, ui } = modelInfo.value;

    const pkField = Object.values(fields_info).find((field: any) => field.is_pk) as Recordable;
    pk.value = pkField.field_name || '';

    // 加载搜索组件
    if (ui.search_fields.length > 0) {
      const search_fields: any = ui.search_fields.map((item: string) => {
        return fields_info[item];
      });
      const component: any = await SearchFieldComponent(search_fields);
      schemas.value.push(component);
    }
    // 加载过滤组件
    // for Each  处理异步会导致顺序不一致
    for (const item of ui.list_filter) {
      const field = fields_info[item];
      if (field.field_type in FilterFieldComponentMap) {
        const component = await FilterFieldComponentMap[field.field_type](field);
        schemas.value.push(component);
      } else {
        console.log(`数据库类型 ${field.field_type} 不支持filter组件化。`);
      }
    }
    // 根据 display_fields 加载表格列配置
    const display_fields = (ui?.list_display || []).includes('*')
      ? Object.keys(fields_info)
      : ui?.list_display || [];
    columns.value = display_fields
      .map((field_name: string) => {
        const field = fields_info[field_name];
        const field_group1 = ['ManyToManyFieldInstance', 'BackwardFKRelation'];
        const field_group2 = ['ForeignKeyFieldInstance', 'OneToOneFieldInstance'];
        // if (field.field_type === 'ManyToManyFieldInstance') {
        if (field_group1.includes(field.field_type)) {
          console.log(
            `[${field.field_type}:${field.field_name}] m2m/bac_fk field need not to be rendered.`
          );
          return null;
        }
        if (field.source_field && !field_group2.includes(field.field_type)) {
          console.log(
            `[${field.field_type}:${field.field_name}] FK field id need not to be rendered.`
          );
          return null;
        }
        if (field.field_type in columnRenderMap) {
          return columnRenderMap[field.field_type](field);
        } else {
          // console.log(`[${field.field_type}]:${field.field_name} default renderer.`);
          return columnRenderMap.default(field);
        }
      })
      .filter((item) => item !== null);
  });

  // 离开组件的钩子函数
  onUnmounted(() => {
    // console.log(`@@@crud_edit:${appName.value}:${modelName.value} onUnmounted`);
  });

  // 激活组件的钩子函数
  onActivated(() => {
    if (crudRefresh.getRefreshFlag(appName.value, modelName.value)) {
      reloadTable();
      crudRefresh.clearRefreshFlag(appName.value, modelName.value);
    }
  });

  // 离开组件的钩子函数
  onDeactivated(() => {
    // console.log('@@@crud_list:${appName.value}:${modelName.value} onDeactivated');
  });
</script>

<style lang="less" scoped>
  .condition-card {
    // margin-bottom: 12px;
    margin-top: 6px;
    .n-card-header {
      padding: 10px 100px;
    }
    .n-card-body {
      padding: 10px 16px;
    }
  }

  // 添加模态框样式
  :deep(.custom-modal) {
    .n-modal {
      width: 600px;
    }

    .n-dialog__content {
      padding: 0;
      background-color: #fff;
    }
  }

  .modal-content {
    max-height: 60vh;
    overflow-y: auto;
    padding: 16px 24px;
  }
</style>
