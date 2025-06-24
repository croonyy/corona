import { GetFieldDistinctValues } from '@/api/crud/models';
import { ref } from 'vue';
import { SelectOption } from 'naive-ui';
import { search_component_key } from './compsSearch';
import { timestampFormat } from './tools';
import { debounce } from 'lodash-es';
// import { number } from 'vue-types';

async function SelectorGenerator(field: any) {
  const loadingRef = ref(false);
  const Focused = ref(false); // 是否已经聚焦过
  const optionsRef = ref<SelectOption[]>([]);
  const totalPages = ref(0);
  const currentQuery = ref('');
  const params = {
    app_model_name: `${field.app_name}:${field.model_name}`,
    field_names: field.field_name,
    paginator: {
      curr_page: 1,
      page_size: 20,
      order_by: [],
      filters: [],
    },
  };

  const loadData = async () => {
    if (!Focused.value) return;
    loadingRef.value = true;
    // console.log(params);
    try {
      const { data } = await GetFieldDistinctValues(params);
      totalPages.value = data.paginator.page_cnt;
      const newOptions = data.values.map((value: any) => {
        // 处理布尔类型 将布尔值转换为字符串
        if (typeof value === 'boolean') return { label: value ? '是' : '否', value: String(value) };
        // 处理其他类型统一转换为字符串
        return { label: value, value: value };
      });
      optionsRef.value.push(...newOptions);
      console.log(
        [
          `${field.field_name.padEnd(15, '-')}`,
          `${String(data.paginator.total).padStart(10, '-')}条`,
          `${String(totalPages.value).padStart(4, '-')}页，`,
          `每页${String(params.paginator.page_size).padStart(4, '-')}条，`,
          `加载第${String(params.paginator.curr_page).padStart(8, '-')}页，`,
        ].join('')
      );
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      loadingRef.value = false;
    }
  };

  // 创建防抖搜索函数
  const debouncedSearch = debounce((query: string) => {
    console.log('onSearch', query);
    // 如果当前查询与新查询相同，则不进行任何操作
    if (currentQuery.value === query && query != '') return;
    currentQuery.value = query;
    params.paginator.filters = query
      ? ([{ field: field.field_name, symbol: 'icontains', value: query }] as any)
      : [];
    optionsRef.value = [];
    params.paginator.curr_page = 1;
    loadData();
  }, 300);

  return {
    field: field.field_name,
    component: 'NSelect',
    label: field.ud_name || field.field_name,
    loading: loadingRef,
    componentProps: {
      placeholder: `请选择${field.ud_name || field.field_name}`,
      filterable: true, // 开启搜索功能
      remote: true, // 开启远程搜索
      tag: true, // 是否可以创建新的选项，需要和 filterable 一起使用
      options: optionsRef, // 设置选项
      loading: loadingRef, // 设置加载状态
      clearable: true, // 用户清除输入的值
      // keyboard: true, // 开启键盘操作
      // clearFilterAfterSelect: false,
      showOnFocus: true,
      onSearch: (query: string) => {
        // 使用防抖搜索函数
        debouncedSearch(query);
      },
      onScroll: async (e) => {
        const target = e.target as HTMLElement;
        const { scrollTop, scrollHeight, clientHeight } = target;
        const oldScrollTop = scrollTop; // 保存当前滚动位置

        const buffer = 5;
        if (scrollTop + clientHeight + buffer >= scrollHeight) {
          if (params.paginator.curr_page < totalPages.value && !loadingRef.value) {
            params.paginator.curr_page += 1;
            // await loadData(false);
            await loadData();
            // 在数据加载完成后恢复滚动位置
            requestAnimationFrame(() => {
              target.scrollTop = oldScrollTop;
            });
          }
        }
      },
      onFocus: () => {
        console.log('onFocus', currentQuery.value);
        if (!Focused.value) {
          // 如果是第一次聚焦，则加载第一页数据，并设置为已经聚焦过，不是第一次聚焦，通过滚动触发后续数据加载
          Focused.value = true;
          loadData();
          // } else if (currentQuery.value == '') {
          //   // 如果当前查询为空，则清空选项，并加载第一页数据，处理清空输入框的情况不保留上次查询结果
          //   optionsRef.value = [];
          // loadData();
        } else {
          return;
        }
      },
      onClear: () => {
        optionsRef.value = [];
        params.paginator.curr_page = 1;
        params.paginator.filters = [];
        currentQuery.value = '';
        loadData();
      },
      // onUpdated: (value: string) => {
      //   console.log(value);
      // },
    },
  };
}

function DatetimeFieldFilter(field: any) {
  return {
    field: field.field_name,
    component: 'NDatePicker',
    label: field.ud_name || field.field_name,
    componentProps: {
      type: 'datetimerange',
      format: 'yyyy-MM-dd HH:mm:ss', // 控制前端显示格式
    },
  };
}

function DateFieldFilter(field: any) {
  return {
    field: field.field_name,
    component: 'NDatePicker',
    label: field.ud_name || field.field_name,
    componentProps: {
      type: 'daterange',
      format: 'yyyy-MM-dd', // 控制前端显示格式
    },
  };
}

export function GenerateFilter(values: any, modelInfo: any) {
  const search_filter: FilterGroup[] = [];
  const filter_list: FilterElement[] = [];
  const type_groups = {
    stringLike: new Set([
      'BigIntField',
      'BinaryField',
      'CharEnumFieldInstance',
      'CharField',
      'DecimalField',
      'FloatField',
      'IntEnumFieldInstance',
      'IntField',
      'SmallIntField',
      'TextField',
      // 'TimeDeltaField', // 时间差字段,数据库存取的是微秒，查出来的值是秒，查询的时候要乘以10的6次方转化为微秒
      'UUIDField',
    ]),
    datetimeLike: new Set(['DateField', 'DatetimeField']),
    booleanLike: new Set(['BooleanField']),
    // numberLike: new Set(['DecimalField', 'FloatField', 'IntegerField', 'SmallIntField']),
    // uuidLike: new Set(['UUIDField']),
  };
  for (const [field_name, value] of Object.entries(values)) {
    if (!value) continue; // Skip empty values
    const field = modelInfo.value.fields_info[field_name];
    const search_fields = modelInfo.value.ui.search_fields;
    // 先组装所有的字符串搜索条件
    if (field_name === search_component_key) {
      const querys: FilterCondition[] = search_fields.map((item) => {
        return { field: item, symbol: 'icontains', value };
      });
      if (querys.length > 0) {
        search_filter.push(['or', ...querys] as FilterGroup);
      }
      continue;
    }

    // 如果字段找不到就直接跳过
    if (!field) continue;

    // 分类讨论字段类型对应的条件形式
    if (type_groups.stringLike.has(field.field_type)) {
      filter_list.push({
        field: field_name,
        symbol: 'eq',
        value,
      });
    }
    if (type_groups.datetimeLike.has(field.field_type)) {
      if (!Array.isArray(value)) continue;
      const new_value = value.map((item: any) => timestampFormat(item));
      const [start, end] = new_value;
      if (start && end) {
        filter_list.push({
          field: field_name,
          symbol: 'range',
          value: [start, end],
        });
      }
    }
    if (type_groups.booleanLike.has(field.field_type)) {
      filter_list.push({
        field: field_name,
        symbol: 'eq',
        value: value == 'true' ? true : false,
      });
    }
    if (field.field_type == 'TimeDeltaField') {
      filter_list.push({
        field: field_name,
        // symbol: 'eq',
        symbol: 'icontains', // 时间差字段,传入查询的时候，会装换为timedelta对象，不是一个整数，需要用相似查询不能用eq
        value: Number(value) * 1000000,
      });
    }
  }

  // 组合搜索和筛选条件
  if (search_filter.length || filter_list.length) {
    const filterGroup: FilterGroup = ['and', ...search_filter, ...filter_list];
    return filterGroup;
  } else {
    return [];
  }
}

export const FilterFieldComponentMap = {
  BigIntField: SelectorGenerator,
  // BinaryField: SelectorGenerator,
  BooleanField: SelectorGenerator,
  CharEnumFieldInstance: SelectorGenerator,
  CharField: SelectorGenerator,
  DateField: DateFieldFilter,
  DatetimeField: DatetimeFieldFilter,
  DecimalField: SelectorGenerator,
  FloatField: SelectorGenerator,
  IntEnumFieldInstance: SelectorGenerator,
  IntField: SelectorGenerator,
  // JSONField: SelectorGenerator,
  SmallIntField: SelectorGenerator,
  TextField: SelectorGenerator,
  TimeDeltaField: SelectorGenerator,
  TimeField: SelectorGenerator,
  UUIDField: SelectorGenerator,
  // ManyToManyFieldInstance: 'NInput',
  // ForeignKeyFieldInstance: 'NInput',
};
