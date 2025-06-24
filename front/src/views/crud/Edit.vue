<template>
  <div class="edit-container">
    <n-card :bordered="false" class="edit-card">
      <n-page-header :subtitle="''">
        <template #title>编辑记录</template>
      </n-page-header>
      <br />
      <div v-if="formLoading" class="form-skeleton">
        <div v-for="i in 8" :key="i" style="margin-bottom: 24px">
          <div
            style="
              display: flex;
              align-items: center;
              justify-content: flex-start;
              gap: 4px;
              margin-bottom: 8px;
            "
          >
            <n-skeleton text style="width: 20%" />
            <n-skeleton text style="width: 40%" />
          </div>
          <n-skeleton text style="width: 100%" />
        </div>
      </div>
      <n-form
        v-else
        ref="formRef"
        :model="formData"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
        :rules="rules"
        :key="formResetKey"
      >
        <n-form-item
          v-for="item in formItems"
          :key="item.field.field_name"
          :path="item.field.field_name"
          :required="item.field.is_required"
        >
          <template #label>
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 4px">
              <span>{{ item.field.ud_name || item.field.field_name }}</span>
              <n-icon color="#999" :title="item.field.field_type">
                <component :is="fieldTypeIcons[item.field.field_type] || fieldTypeIcons.Default" />
              </n-icon>
            </div>
          </template>
          <div style="display: flex; flex-direction: column; width: 100%">
            <component
              :is="item.component || 'NInput'"
              ref="{{item.field.app_name}}:{{item.field.model_name}}:{{item.field.field_name}}"
              v-model:value="formData[item.field.field_name]"
              v-bind="{
                ...item.componentProps,
                disabled: item.field.read_only || item.field.is_pk,
              }"
              style="align-self: flex-start"
            />
            <div style="color: #999; font-size: 12px">{{ item.field.description }}</div>
          </div>
        </n-form-item>
      </n-form>
    </n-card>
    <div class="floating-buttons">
      <n-button type="primary" @click="handleSubmit()" size="small">保存并关闭</n-button>
      <n-button type="success" @click="handleSaveOnly()" size="small">保存并继续编辑</n-button>
      <n-button type="success" @click="handleSaveAndAddAnother()" size="small"
        >保存并增加另一个</n-button
      >
      <n-button type="error" @click="handleDelete()" size="small" :focusable="false">删除</n-button>
      <n-button @click="handleClearForm" size="small">清空数据</n-button>
      <n-button @click="handleCancel" size="small">取消</n-button>
      <!-- <n-button @click="test" size="small">测试</n-button> -->
    </div>
  </div>
</template>
<script setup lang="ts">
  import { ref, onMounted, toRaw, onActivated } from 'vue';
  import {
    createFormRules,
    FormItemFieldComponentMap,
    getObjChangedFields,
    FrontendMod,
    BackendMod,
  } from './compsForm';
  import { fieldTypeIcons } from './columnRender';
  import { useRoute, useRouter } from 'vue-router';
  import {
    GetAllowModelInfo,
    GetModelItem,
    UpdateModelItem,
    DeleteModelItem,
    FetchManage,
  } from '@/api/crud/models';
  import { CRUD_CREATE, CRUD_EDIT, CRUD_LIST } from '@/store/consts';
  import { useTabsViewStore } from '@/store/modules/tabsView';
  // import { useEventBus } from '@vueuse/core';
  import { cloneDeep } from 'lodash-es';
  import { useCrudRefresh } from '@/store/modules/crudListRefresh';

  defineOptions({
    name: CRUD_EDIT,
  });

  // 表单和状态
  const formLoading = ref(false);
  const modelInfo = ref();
  const currentRecord = ref<Recordable>({});
  const formRef = ref();
  const formData = ref({});
  const formResetKey = ref(0);
  // const isEdit = ref(false);
  const formItems = ref<Recordable[]>([]);
  const pk = ref<string>('');
  const fk = ref<Array<string>>([]);
  // 路由和存储
  const route = useRoute();
  const router = useRouter();
  const crudRefresh = useCrudRefresh();
  const tabsViewStore = useTabsViewStore();
  const appName = ref('');
  const modelName = ref('');
  const objId = ref('');
  const rules = ref({});
  const initialData = {};
  const saveCount = ref(0);

  const FkField = ['ForeignKeyFieldInstance', 'OneToOneFieldInstance'];

  // ==================== 数据操作辅助函数 ====================

  // 更新已有记录
  async function updateRecord() {
    const data_before = toRaw(currentRecord.value);
    const data_after = toRaw(formData.value);
    const changedFields = getObjChangedFields(data_before, data_after);
    if (Object.keys(changedFields).length === 0) {
      window['$message'].warning('没有修改任何内容');
      return false;
    }
    const { commFields, m2mFields } = BackendMod(changedFields, modelInfo.value.fields_info);
    for (const [field_name, items] of Object.entries(m2mFields)) {
      const { add, del } = items as any;
      if (add.length > 0 || del.length > 0) {
        const m2m_ids: any = {
          add: add.map((item) => item.value),
          del: del.map((item) => item.value),
        };
        const params = {
          action: 'manage',
          field_name,
          id: toRaw(objId.value),
          m2m_ids: toRaw(m2m_ids),
        };
        await FetchManage(appName.value, modelName.value, params);
      }
    }

    try {
      await UpdateModelItem(appName.value, modelName.value, currentRecord.value?.id, commFields);
      window['$message'].success('修改成功');
      currentRecord.value = cloneDeep(data_after);

      // 通知列表刷新
      crudRefresh.setRefreshFlag(appName.value, modelName.value);
      return true;
    } catch (error: any) {
      console.error('修改失败:', error);
      window['$message'].error('修改失败: ' + (error.message || '未知错误'));
      return false;
    }
  }

  function modelListPage() {
    tabsViewStore.closeCurrentTab(route as any);
    router.push({
      name: CRUD_LIST,
      params: { app_name: appName.value, model_name: modelName.value },
    });
  }

  async function formValidate() {
    try {
      await formRef.value.validate();
    } catch (error) {
      console.log(error);
      window['$message'].error('存在未通过验证的字段');
      throw error;
    }
  }

  // ==================== 按钮处理函数 ====================

  // 保存并关闭
  async function handleSubmit() {
    await formValidate();
    const success = await updateRecord();
    if (success) {
      formResetKey.value++;
      modelListPage();
    }
  }

  // 保存并继续编辑
  async function handleSaveOnly() {
    await formValidate();
    await updateRecord();
    // 通过改变子组件监控的数据通知子组件更新数据
    saveCount.value += 1;
    // router刷新页面
    // router.go(0);
    await updateItemValues(modelInfo.value.fields_info, fk.value);
  }

  // 保存并增加另一个
  async function handleSaveAndAddAnother() {
    await formValidate();
    let success = false;
    success = await updateRecord();
    if (success) {
      tabsViewStore.closeCurrentTab(route as any);
      router.push({
        name: CRUD_CREATE,
        params: {
          app_name: appName.value,
          model_name: modelName.value,
        },
      });
    }
  }

  // 删除记录
  function handleDelete() {
    window['$dialog'].warning({
      title: '确认删除',
      content: '确定要删除此记录吗？此操作不可恢复。',
      positiveText: '确认删除',
      negativeText: '取消',
      autoFocus: false,
      onPositiveClick: async () => {
        try {
          await DeleteModelItem(appName.value, modelName.value, currentRecord.value?.id);
          window['$message'].success('删除成功');
          tabsViewStore.closeCurrentTab(route as any);
          await router.push({
            name: CRUD_LIST,
            params: { app_name: appName.value, model_name: modelName.value },
          });
          crudRefresh.setRefreshFlag(appName.value, modelName.value);
        } catch (error: any) {
          console.error('删除失败:', error);
          window['$message'].error('删除失败: ' + (error.message || '未知错误'));
        }
      },
    });
    crudRefresh.setRefreshFlag(appName.value, modelName.value);
  }
  // 清空数据
  function handleClearForm() {
    // console.log('initialData', initialData);
    formData.value = cloneDeep(initialData);
    // 强制表单重新渲染
    formResetKey.value++;
  }

  // 取消
  function handleCancel() {
    router.push({
      name: CRUD_LIST,
      params: { app_name: appName.value, model_name: modelName.value },
    });
    crudRefresh.setRefreshFlag(appName.value, modelName.value);
    tabsViewStore.closeCurrentTab(route as any);
  }

  // 测试
  async function test() {
    console.log('!!!!!!!!!!!!!!', toRaw(formData.value));
    await formValidate();
    console.log('!!!!!!!!!!!!!!', toRaw(formData.value));
  }

  // 生成表单项配置
  async function generateFormItems(model_info, id) {
    const { fields_info, ui } = model_info.value;
    if (!fields_info) return [];
    const items: any[] = [];
    // 根据 display_fields 加载表格列配置
    const display_fields = (ui?.list_display || []).includes('*')
      ? Object.keys(fields_info)
      : ui?.list_display || [];
    // 使用 for...of 循环，这样可以按顺序处理每个字段
    // for (const item of Object.values(fields_info)) {
    // 添加类型断言，定义 field 的类型
    // const field = item as { field_type: string; field_name: string };
    // const field = item as Recordable;
    for (const field_name of display_fields) {
      const field = fields_info[field_name];
      // if (field.is_pk) continue; // 跳过主键字段，主键字段不需要在表单中显示，也不能修改
      const field_group1 = ['ForeignKeyFieldInstance', 'OneToOneFieldInstance'];
      if (field.source_field && !field_group1.includes(field.field_type)) {
        console.log(
          `[${field.field_type}:${field.field_name}] FK field id need not to be edit derectly.`
        );
        continue;
      }
      if (field.field_type in FormItemFieldComponentMap) {
        try {
          let result: any = null;
          const relation_search = ui.relation_search[field.field_name] || ['id'];
          const types_group1 = ['ForeignKeyFieldInstance', 'ManyToManyFieldInstance'];
          if (types_group1.includes(field.field_type)) {
            result = FormItemFieldComponentMap[field.field_type](
              field,
              id,
              relation_search,
              saveCount
            );
          } else if (FkField.includes(field.field_type)) {
            console.log('formData', formData.value);
            result = FormItemFieldComponentMap[field.field_type](field, id, relation_search);
          } else {
            result = FormItemFieldComponentMap[field.field_type](field);
          }
          // 等待包含下拉框的组件的异步Promise完成或直接使用结果
          // const item = await (result instanceof Promise ? result : Promise.resolve(result));
          const item = result instanceof Promise ? await result : result;
          if (item) items.push(item);
        } catch (error) {
          console.error(`生成表单项配置时处理字段 ${field.field_name} 时出错:`, error);
        }
      } else {
        console.log(`[${field.field_type}:${field.field_name}] 不支持formItem组件化。`);
      }
    }
    return items; // 直接返回对象列表，不是 Promise
  }

  async function updateItemValues(fields_info, fk) {
    const { data } = await GetModelItem(appName.value, modelName.value, objId.value);
    const tmp = FrontendMod(data, modelInfo.value.fields_info);
    currentRecord.value = cloneDeep(tmp);
    console.log('@@@currentRecord', currentRecord.value);
    formData.value = tmp;
    initialData[pk.value] = tmp[pk.value];
    console.log('@@@initialData', initialData);
    // 设置外键默认值
    fk.forEach((field_name) => {
      formData.value[field_name] = currentRecord.value[fields_info[field_name].source_field];
      currentRecord.value[field_name] = tmp[field_name];
    });
  }
  // 初始化
  onMounted(async () => {
    // 获取路由参数
    appName.value = route.params.app_name as string;
    modelName.value = route.params.model_name as string;
    objId.value = route.params.id as string;

    // 加载模型信息
    const { data: model_info_data } = await GetAllowModelInfo({
      model_name: `${appName.value}:${modelName.value}`,
    });
    modelInfo.value = model_info_data;
    console.log('@@@modelInfo', toRaw(modelInfo.value));

    const { fields_info } = modelInfo.value;
    // let fk = [] as string[];
    // const pkField = Object.values(fields_info).find((field: any) => field.is_pk) as Recordable;
    Object.values(fields_info).forEach((field: any, _) => {
      if (field.is_pk) {
        pk.value = field.field_name;
      }
      if (FkField.includes(field.field_type)) {
        fk.value.push(field.field_name);
      }
    });

    // 生成表单和规则
    formItems.value = await generateFormItems(modelInfo, objId.value);
    rules.value = createFormRules(fields_info) || {};

    // 初始化字段默认值
    formItems.value.forEach((item) => {
      if (item.field.field_type === 'BooleanField') {
        initialData[item.field_name] = item.default || false;
        // } else if (item.field.is_pk) {
        //   initialData[item.field_name] = item.default;
      } else {
        if (item.default) {
          initialData[item.field_name] = item.default;
        }
      }
    });
    formData.value = cloneDeep(initialData);

    // 加载编辑模式数据
    formLoading.value = true;
    try {
      await updateItemValues(fields_info, fk.value);
      // formData.value['user'] = 3;
    } catch (error) {
      console.error('获取记录详情失败:', error);
      window['$message'].error('获取记录详情失败');
    } finally {
      formLoading.value = false;
    }
  });
  onActivated(() => {
    // console.log('edit onActivated', route.fullPath);
  });
</script>
<style lang="less" scoped>
  .edit-container {
    position: relative;
    min-height: 100%;
    padding-bottom: 80px; /* 为底部按钮留出空间 */
  }

  .floating-buttons {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
    z-index: 100;
    background-color: white;
    padding: 5px 5px;
    border-radius: 4px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    width: fit-content;
    margin: 0 auto;
  }

  .edit-card {
    margin-top: 6px;
  }
</style>
