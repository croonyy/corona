<template>
  <div class="transfer-list-container" :value="[...addList, ...delList]">
    <div class="list-box">
      <div class="title"
        >可选关系
        <n-popover trigger="hover" placement="right-end">
          <template #trigger>
            <span class="help help-tooltip help-icon">
              <QuestionCircleFilled style="display: inline; height: 16px" />
            </span>
          </template>
          选入待处理关系以等待赋予。
        </n-popover>
      </div>
      <div class="list-header">
        <n-input
          v-model:value="leftSearch"
          placeholder="搜索..."
          clearable
          @update:value="debouncedLeftSearch"
        />
      </div>
      <div class="list-content">
        <!-- <n-scrollbar @scroll="handleLeftScroll"> -->
        <n-scrollbar @scroll="debouncedLeLeftScroll">
          <n-spin :show="leftLoading">
            <!-- 当filteredLeftList为空的时候显示一个没有数据的图标 -->
            <!-- <div v-if="filteredLeftList.length === 0" class="no-data">暂无数据</div> -->
            <div v-if="filteredLeftList.length === 0" class="no-data">
              <n-flex vertical align="center" justify="center" style="height: 200px">
                <n-icon size="48">
                  <DropboxOutlined />
                </n-icon>
                <span style="margin-top: 8px">暂无数据</span>
              </n-flex>
            </div>
            <div v-for="item in filteredLeftList" :key="item.value" class="list-item">
              <option value="{{ item.value }}" :title="item.label" @click="addItem(item)">
                {{ item.label }}
              </option>
              <!-- <span @click="addItem(item)">{{ item.label }}</span> -->
            </div>
          </n-spin>
        </n-scrollbar>
      </div>
    </div>
    <div class="list-box">
      <div class="title"
        >已存在的关系
        <n-popover trigger="hover" placement="right-end">
          <template #trigger>
            <span class="help help-tooltip help-icon">
              <QuestionCircleFilled style="display: inline; height: 16px" />
            </span>
          </template>
          选入待处理关系以等待删除。
        </n-popover>
      </div>
      <div class="list-header">
        <n-input
          v-model:value="rightSearch"
          placeholder="搜索..."
          clearable
          @update:value="debouncedRightSearch"
        />
      </div>
      <div class="list-content">
        <n-scrollbar @scroll="debouncedLeRightScroll">
          <n-spin :show="rightLoading">
            <div v-if="filteredRightList.length === 0" class="no-data">
              <n-flex vertical align="center" justify="center" style="height: 200px">
                <n-icon size="48">
                  <DropboxOutlined />
                </n-icon>
                <span style="margin-top: 8px">暂无数据</span>
              </n-flex>
            </div>
            <div v-for="item in filteredRightList" :key="item.value" class="list-item">
              <span @click="delItem(item)">{{ item.label }}</span>
            </div>
          </n-spin>
        </n-scrollbar>
      </div>
    </div>
    <div class="list-box">
      <div class="title">
        待处理关系
        <n-popover trigger="hover" placement="right-end">
          <template #trigger>
            <span class="help help-tooltip help-icon">
              <QuestionCircleFilled style="display: inline; height: 16px" />
            </span>
          </template>
          待处理的关系，点击保存后生效，绿底为待追加的关系，红底为待删除的关系。
        </n-popover>
      </div>
      <div class="list-content">
        <n-scrollbar>
          <div
            v-for="item in [...addList, ...delList]"
            :key="item.value"
            class="list-item"
            :style="{ backgroundColor: item.isDel ? '#f4b4b4' : '#b4f4b4' }"
          >
            <!-- <n-checkbox :value="item.value" :label="item.label" @click="test" /> -->
            <span @click="clearItem(item)">{{ item.label }}</span>
          </div>
        </n-scrollbar>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, watchEffect, onMounted, toRaw, watch } from 'vue';
  import { QuestionCircleFilled } from '@vicons/antd';
  import { debounce } from 'lodash-es';
  import { useMessage } from 'naive-ui';
  import { FetchManage } from '@/api/crud/models';
  import { DropboxOutlined } from '@vicons/antd';

  const message = useMessage();

  const props = withDefaults(
    defineProps<{
      // value: ModelValue;
      field: Recordable;
      id?: string;
      relationSearch: Array<string>;
      saveCount;
    }>(),
    {
      // value: () => ({}),
    }
  );

  const emit = defineEmits<{
    (e: 'update:value', value: ModelValue): void;
  }>();

  const leftList = ref<TransferItem[]>([]);
  const rightList = ref<TransferItem[]>([]);
  const leftSearch = ref('');
  const rightSearch = ref('');
  const leftLoading = ref(false);
  const rightLoading = ref(false);
  const paramsLeft = ref(getFetchManageParams('list'));
  const paramsRight = ref(getFetchManageParams('query'));
  const leftPaginator = ref<Record<string, any>>({});
  const rightPaginator = ref<Record<string, any>>({});
  const addList = ref<TransferItem[]>([]);
  const delList = ref<TransferItem[]>([]);
  const relationSearch: Array<string> =
    props.relationSearch.length > 0 ? props.relationSearch : ['id'];

  function getFetchManageParams(action: string): FatchManageParams {
    return {
      action,
      field_name: props.field.field_name,
      label: true,
      id: props.id,
      paginator: {
        curr_page: 1,
        page_size: 100,
        order_by: [],
        filters: [],
      },
      m2m_ids: {},
    };
  }
  function clearItem(item: any) {
    console.log('clearItem', item);
    if (item.isDel) {
      delList.value = delList.value.filter((i) => i.value !== item.value);
    } else {
      addList.value = addList.value.filter((i) => i.value !== item.value);
    }
  }

  function addItem(item: any) {
    console.log('addItem', item);
    if (addList.value.filter((i) => i.value == item.value).length == 0) {
      addList.value.push({ ...item, isDel: false });
    } else {
      message.info('已选择', {});
    }
  }
  function delItem(item: any) {
    console.log('delItem', item);
    if (delList.value.filter((i) => i.value == item.value).length == 0) {
      delList.value.push({ ...item, isDel: true });
    } else {
      message.info('已选择');
    }
  }

  watchEffect(() => {
    const newValue = {
      add: toRaw(addList.value),
      del: toRaw(delList.value),
    };
    emit('update:value', newValue);
  });

  watch(
    () => props.saveCount,
    async (newVal) => {
      console.log('saveCount', newVal);
      if (newVal) {
        // 保存之后 更新数据,并清空tmp框
        await reloadRightData();
      }
    }
  );

  const reloadRightData = debounce(async () => {
    await fetchRightData();
    addList.value = [];
    delList.value = [];
  }, 300);

  async function fetchLeftData() {
    const { data, extra } = await FetchManage(
      props.field.app_name,
      props.field.model_name,
      paramsLeft.value
    );
    const results = data.map((item: any) => ({ label: item.label, value: item.value.id }));
    // const results = await props.onLeftSearch(value);
    leftList.value = results;
    leftPaginator.value = extra.paginator;
  }
  async function fetchRightData() {
    const { data, extra } = await FetchManage(
      props.field.app_name,
      props.field.model_name,
      paramsRight.value
    );
    const results = data.map((item: any) => ({ label: item.label, value: item.value.id }));
    // const results = await props.onLeftSearch(value);
    rightList.value = results;
    rightPaginator.value = extra.paginator;
  }

  // 搜索处理函数
  const handleLeftSearch = async (value: string) => {
    leftLoading.value = true;
    try {
      const querys: FilterGroup = [
        'or',
        ...relationSearch.map((item) => ({
          field: item,
          symbol: 'icontains',
          value,
        })),
      ];
      paramsLeft.value.field_name = props.field.field_name;
      paramsLeft.value.action = 'query';
      paramsLeft.value.paginator.curr_page = 1;
      paramsLeft.value.paginator.filters = querys;
      await fetchLeftData();
    } catch (error) {
      console.error('左侧搜索失败:', error);
    } finally {
      leftLoading.value = false;
    }
  };

  const handleRightSearch = async (value: string) => {
    console.log('handleRightSearch', Boolean(props.id));
    // 没有id的情况下直接返回
    if (!Boolean(props.id)) {
      return;
    }
    rightLoading.value = true;
    try {
      const querys: FilterGroup = [
        'or',
        ...relationSearch.map((item) => ({
          field: item,
          symbol: 'icontains',
          value,
        })),
      ];
      paramsRight.value.field_name = props.field.field_name;
      paramsRight.value.action = 'list';
      paramsRight.value.paginator.curr_page = 1;
      paramsRight.value.paginator.filters = querys;
      await fetchRightData();
    } catch (error) {
      console.error('右侧搜索失败:', error);
    } finally {
      rightLoading.value = false;
    }
  };

  // 处理滚动事件
  const handleLeftScroll = async (e: Event) => {
    console.log('左侧滚动:');
    const target = e.target as HTMLElement;
    const { scrollTop, scrollHeight, clientHeight } = target;
    const oldScrollTop = scrollTop; // 保存当前滚动位置
    const buffer = 5;
    if (scrollTop + clientHeight + buffer >= scrollHeight) {
      if (leftPaginator.value.curr_page < leftPaginator.value.page_cnt && !leftLoading.value) {
        leftLoading.value = true;
        try {
          console.log('加载更多');
          paramsLeft.value.paginator.curr_page += 1;
          const { data, extra } = await FetchManage(
            props.field.app_name,
            props.field.model_name,
            paramsLeft.value
          );
          const results = data.map((item: any) => ({ label: item.label, value: item.value.id }));
          leftList.value.push(...results);
          leftPaginator.value = extra.paginator;
          requestAnimationFrame(() => {
            target.scrollTop = oldScrollTop;
          });
          leftLoading.value = false;
        } catch (error) {
          console.error('加载更多失败:', error);
          leftLoading.value = false;
        }
      }
    }
  };
  const handleRightScroll = async (e: Event) => {
    console.log('右侧滚动:');
    const target = e.target as HTMLElement;
    const { scrollTop, scrollHeight, clientHeight } = target;
    const oldScrollTop = scrollTop; // 保存当前滚动位置
    const buffer = 5;
    if (scrollTop + clientHeight + buffer >= scrollHeight) {
      if (rightPaginator.value.curr_page < rightPaginator.value.page_cnt && !rightLoading.value) {
        rightLoading.value = true;
        try {
          console.log('加载更多');
          paramsRight.value.paginator.curr_page += 1;
          const { data, extra } = await FetchManage(
            props.field.app_name,
            props.field.model_name,
            paramsRight.value
          );
          const results = data.map((item: any) => ({ label: item.label, value: item.value.id }));
          rightList.value.push(...results);
          rightPaginator.value = extra.paginator;
          requestAnimationFrame(() => {
            target.scrollTop = oldScrollTop;
          });
          rightLoading.value = false;
        } catch (error) {
          console.error('加载更多失败:', error);
          rightLoading.value = false;
        }
      }
    }
  };

  // 防抖处理搜索
  const debouncedLeftSearch = debounce(handleLeftSearch, 300);
  const debouncedRightSearch = debounce(handleRightSearch, 300);
  const debouncedLeLeftScroll = debounce(handleLeftScroll, 300);
  const debouncedLeRightScroll = debounce(handleRightScroll, 300);

  // 过滤后的列表（现在主要用于本地过滤）
  const filteredLeftList = computed(() => {
    return leftList.value;
  });

  const filteredRightList = computed(() => {
    return rightList.value;
  });

  onMounted(() => {
    debouncedLeftSearch('');
    debouncedRightSearch('');
  });
</script>

<style scoped>
  .transfer-list-container {
    width: 100%;
    max-width: 1000px;
    display: flex;
    align-items: stretch;
    gap: 4px;
    min-height: 300px;
  }

  .list-box {
    /* min-width: 300px; */
    /* width: 400px; */
    width: 100%;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    display: flex;
    height: 400px;
    flex-direction: column;
    background-color: #ffffff;
  }

  .list-header {
    padding: 4px;
    border-bottom: 1px solid #e5e7eb;
  }

  .title {
    padding: 8px;
    border-bottom: 1px solid #e5e7eb;
    /* font-weight: bold; */
    color: #666;
  }

  .list-content {
    /* flex: 1; */
    /* min-height: 300px; */
    /* max-height: 300px; */
    /* height: 300px; */
    padding: 8px;
    overflow: hidden;
  }

  .list-footer {
    padding: 8px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f9fafb;
  }

  .list-item {
    /* padding: 0px; */
    padding-left: 4px;
    cursor: pointer;
    border-radius: 4px;
    margin-bottom: 0px;
  }
  .list-item > .span {
    display: inline-block !important;
    width: 100%; /* 确保 span 元素填满容器 */
    white-space: nowrap !important; /* 防止文本换行 */
    overflow: hidden; /* 隐藏超出部分 */
    text-overflow: ellipsis; /* 显示省略号 */
    cursor: default; /* 鼠标悬停时显示默认光标 */
  }

  .list-item:hover {
    background-color: #eeeeee;
  }

  .transfer-controls {
    display: flex;
    flex-direction: column;
    gap: 8px;
    justify-content: center;
  }

  /* :deep(.n-checkbox) {
    width: 100%;
  } */

  :deep(.n-checkbox__label) {
    width: 100%;
  }

  .list-item > span {
    display: block;
    margin: 2px;
  }
</style>
