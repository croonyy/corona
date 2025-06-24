import { GetFieldDistinctValues } from '@/api/crud/models';
import { ref, markRaw } from 'vue';
import { SelectOption } from 'naive-ui';
// import { search_component_key } from './compsSearch';
import { timestampFormat, getISOStringWithLocalTimezone } from './tools';
import { debounce } from 'lodash-es';
// import { renderIconTitle, fieldTypeIcons } from './renderList';
// import UdTransferList from '@/components/TransferList/UdTransferList.vue';
import M2m from '@/components/UdFormItem/M2m.vue';
import { FetchManage } from '@/api/crud/models';
// import { ac } from '@faker-js/faker/dist/airline-BcEu2nRk';
// import { number } from 'vue-types';

export const FormItemFieldComponentMap = {
  BigIntField: NumberComponent,
  // BinaryField: SelectorGenerator,
  BooleanField,
  CharEnumFieldInstance: EnumFieldInstanceGenerator,
  CharField,
  DateField,
  DatetimeField,
  DecimalField: DecimalField,
  FloatField: FloatField,
  IntEnumFieldInstance: EnumFieldInstanceGenerator,
  IntField,
  JSONField,
  SmallIntField: IntField,
  TextField,
  // TimeDeltaField: FloatField,
  UUIDField,
  Default: CharField,
  ManyToManyFieldInstance: ManyToManyFieldInstanceGenerator,
  ForeignKeyFieldInstance: ForeignKeyField,
  OneToOneFieldInstance: ForeignKeyField,
  // BackwardFKRelation:,
  // ForeignKeyFieldInstance: 'NInput',
};

export function getObjChangedFields(data_before: Recordable, data_after: Recordable) {
  const changedFields = {};
  for (const key in data_after) {
    // 只对两个对象都包含的键进行比较
    if (key in data_before) {
      // 使用严格比较检查值是否发生变化
      if (JSON.stringify(data_after[key]) !== JSON.stringify(data_before[key])) {
        changedFields[key] = data_after[key];
      }
    } else {
      changedFields[key] = data_after[key];
    }
  }
  return changedFields;
}

export const FrontendMod = (data: any, fields_info: any): Recordable => {
  const tmp = { ...data };
  Object.entries(fields_info).forEach(([key, field]: [string, any]) => {
    // 处理日期字段，将字符串转换为时间戳
    if (field.field_type === 'DateField' || field.field_type === 'DatetimeField') {
      if (tmp[key]) {
        tmp[key] = new Date(tmp[key]).getTime();
      }
    }
    // 处理JSON字段，将对象转换为字符串
    if (field.field_type === 'JSONField') {
      if (typeof tmp[key] === 'object') {
        tmp[key] = JSON.stringify(tmp[key]);
      }
    }
  });
  return tmp;
};

export const BackendMod = (data: Recordable, fields_info: Recordable): Recordable => {
  // 处理日期时间字段,将时间戳转换为日期时间字符串
  const comm = {};
  const m2m = {};
  // Object.entries(fields_info).forEach(([key, field]: [string, any]) => {
  Object.entries(data).forEach(([key, value]: [string, any]) => {
    const field = fields_info[key] || {};
    if (field.field_type === 'DateField') {
      if (value) comm[key] = timestampFormat(value, 'yyyy-MM-dd');
      // if (tmp[key]) tmp[key] = getISOStringWithLocalTimezone(tmp[key]);
    } else if (field.field_type === 'DatetimeField') {
      // if (tmp[key]) tmp[key] = timestampFormat(tmp[key], 'yyyy-MM-dd HH:mm:ss');
      if (value) comm[key] = getISOStringWithLocalTimezone(value);
    } else if (field.field_type === 'ManyToManyFieldInstance') {
      m2m[key] = value;
    } else if (['ForeignKeyFieldInstance', 'OneToOneFieldInstance'].includes(field.field_type)) {
      // fk[key] = value;
      comm[field.source_field] = value;
    } else if (field.field_type === 'JSONField') {
      // 处理JSON字段，将对象转换为字符串
      try {
        comm[key] = value ? JSON.parse(value) : null;
      } catch (error) {
        console.error(`parse JSONField[${key}]: ${comm[key]} failed.`, error);
      }
    } else {
      comm[key] = value;
    }
  });
  return { commFields: comm, m2mFields: m2m };
};

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

  const debouncedScroll = debounce(async (e) => {
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
  }, 300);
  return {
    field,
    component: 'NSelect',
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
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
      // 使用防抖搜索函数
      onSearch: debouncedSearch,
      onScroll: debouncedScroll,
      onFocus: () => {
        console.log('onFocus', currentQuery.value);
        if (!Focused.value) {
          // 如果是第一次聚焦，则加载第一页数据，并设置为已经聚焦过，不是第一次聚焦，通过滚动触发后续数据加载
          Focused.value = true;
          loadData();
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
    },
  };
}
function EnumFieldInstanceGenerator(field: any) {
  const options = field.choices.map((value, key) => {
    return { label: value, value: value };
  });
  return {
    field,
    component: 'NSelect',
    componentProps: {
      options: options,
      placeholder: `请选择${field.ud_name || field.field_name}`,
      filterable: true,
      clearable: true,
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
    },
  };
}

function IntField(field: any) {
  return {
    field,
    component: 'NInputNumber',
    componentProps: {
      precision: 0, // 不允许小数
      step: 1, // 步长为1
      style: { ...{ width: '320px' }, ...field['style'] },
    },
  };
}

function BooleanField(field: any) {
  return {
    field,
    component: 'NSwitch',
    componentProps: {
      style: { ...field['style'] },
      defaultValue: false,
      default: false,
      // value: false,
    },
  };
}

function TextField(field: any) {
  return {
    field,
    component: 'NInput',
    componentProps: {
      type: 'textarea',
      style: { ...{ maxWidth: '600px' }, ...field['style'] },
    },
  };
}

function UUIDField(field: any) {
  return {
    field,
    component: 'NInput',
    componentProps: {
      type: 'text',
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
    },
  };
}

function CharField(field: any) {
  return {
    field,
    component: 'NInput',
    componentProps: {
      type: 'text',
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
    },
  };
}

function JSONField(field: any) {
  return {
    field,
    component: 'NInput',
    componentProps: {
      type: 'textarea',
      style: { ...{ maxWidth: '600px' }, ...field['style'] },
    },
  };
}

function DecimalField(field: any) {
  return {
    field,
    component: 'NInputNumber',
    componentProps: {
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
      showButton: false,
      precision: field.decimal_places, // 小数位数
    },
  };
}

function FloatField(field: any) {
  return {
    field,
    component: 'NInputNumber',
    componentProps: {
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
      required: true,
      showButton: false,
      min: 0.000001, // 设置最小值为一个接近0的正数
      precision: 6, // 设置精度为6位小数
    },
    rules: [
      {
        required: true,
        message: `请输入${field.ud_name || field.field_name}`,
        // trigger: ['blur', 'input'],
      },
      {
        type: 'number',
        min: 0.000001,
        message: '请输入大于0的数字',
        // trigger: ['blur', 'input'],
      },
    ],
  };
}

function DatetimeField(field: any) {
  return {
    field,
    component: 'NDatePicker',
    componentProps: {
      type: 'datetime',
      style: { ...{ width: '220px' }, ...field['style'] },
      // style: { maxWidth: '320px' }, //maxWidth 无效
      format: 'yyyy-MM-dd HH:mm:ss', // 控制前端显示格式
      // valueFormat: 'yyyy-MM-dd HH:mm:ss', // 控制值的格式
      clearable: true,
      // isDateDisabled: (timestamp: number) => {
      //   return timestamp > Date.now();
      // },
    },
    // rules: [
    //   {
    //     required: field.required || false,
    //     message: `请选择${field.ud_name || field.field_name}`,
    //     trigger: ['blur', 'change'],
    //   },
    // ],
  };
}

function DateField(field: any) {
  return {
    field,
    component: 'NDatePicker',
    componentProps: {
      style: { ...{ maxWidth: '400px' }, ...field['style'] },
      type: 'date',
      // format: 'yyyy-MM-dd', // 控制前端显示格式
      valueFormat: 'yyyy-MM-dd', // 控制值的格式
      clearable: true,
    },
    // rules: [
    //   {
    //     required: field.required || false,
    //     message: `请选择${field.ud_name || field.field_name}`,
    //     trigger: ['blur', 'change'],
    //   },
    // ],
  };
}

function NumberComponent(field: any) {
  return {
    field,
    component: 'NInputNumber',
    componentProps: {
      style: { ...{ maxWidth: '320px' }, ...field['style'] },
    },
  };
}

// function ManyToManyFieldInstanceGenerator(field: any) {
//   function createOptions() {
//     return Array.from({ length: 5 }).map((_, i) => ({
//       label: `Option ${i}`,
//       value: i,
//     }));
//   }
//   const tvalue = ref<Recordable[]>([]);

//   return {
//     field,
//     component: 'NTransfer',
//     componentProps: {
//       style: field['style'] || {
//         width: '800px',
//       },
//       value: tvalue,
//       'onUpdate:value': (newValue: Recordable[]) => {
//         tvalue.value = newValue;
//       },
//       options: createOptions(),
//       sourceFilterable: true,
//       targetFilterable: true,
//       // filter: (value: any, filter: any, from: any) => {
//       //   console.log(value, filter, from);
//       //   return true;
//       // },
//     },
//   };
// }

export function getFetchManageParams(): FatchManageParams {
  return {
    action: 'list',
    field_name: '',
    label: true,
    id: 1,
    paginator: {
      curr_page: 1,
      page_size: 20,
      order_by: [],
      filters: [],
    },
    m2m_ids: [],
  };
}

async function ManyToManyFieldInstanceGenerator(
  field: any,
  id: number,
  relation_search: Array<string>,
  saveCount
) {
  return {
    field,
    // component: UdTransferList,
    component: markRaw(M2m),
    componentProps: {
      field,
      id,
      relationSearch: relation_search,
      saveCount,
    },
  };
}

// async function ForeignKeyField(field: any, id: number) {
//   // const selectedValue = ref<string | number | null>(null); // 用于存储选中的值
//   // const loadingRef = ref(false);
//   // // const optionsRef = ref<SelectOption[]>([]);
//   // const optionsRef = ref<SelectOption[]>([{ label: 'aaa', value: 3 }]);

//   return {
//     field,
//     component: markRaw(ForeignKey),
//     // loading: loadingRef,
//     componentProps: {
//       field,
//       id,
//     },
//   };
// }

async function ForeignKeyField(field: any, id: string, relation_search: Array<string>) {
  const loadingRef = ref(false);
  const searchStr = ref('');
  // const optionsRef = ref<SelectOption[]>([]);
  const optionsRef = ref<SelectOption[]>([]);
  const totalPages = ref(0);
  const params = ref(<Recordable>{});

  params.value = {
    action: 'list',
    label: true,
    field_name: field.field_name,
    id: id,
    paginator: {
      curr_page: 1,
      page_size: 10,
      order_by: [],
      filters: [] as FilterGroup | [],
    },
  };
  // 初始化组件
  if (id) {
    params.value.action = 'list';
    params.value.id = id;
    const { data: default_option } = await FetchManage(
      field.app_name,
      field.model_name,
      params.value
    );
    optionsRef.value =
      default_option.map((item: any) => ({
        label: item.label,
        value: item.value.id,
      })) || [];
  }
  // 创建防抖搜索函数
  const debouncedSearch = debounce(async (query: string) => {
    console.log('onSearch', query);
    const querys: FilterGroup = [
      'or',
      ...relation_search.map((item) => ({
        field: item,
        symbol: 'icontains',
        value: query,
      })),
    ];
    params.value.action = 'query';
    // @ts-ignore
    params.value.paginator.filters = querys;
    params.value.paginator.curr_page = 1;
    loadingRef.value = true;
    const { data, extra } = await FetchManage(field.app_name, field.model_name, params.value);
    optionsRef.value = data.map((item: any) => ({ label: item.label, value: item.value.id }));
    totalPages.value = extra.paginator.page_cnt;
    loadingRef.value = false;
  }, 300);
  debouncedSearch(''); // 默认搜索一次

  // 创建防滚动函数
  const debouncedScroll = debounce(async (e: any) => {
    const target = e.target as HTMLElement;
    const { scrollTop, scrollHeight, clientHeight } = target;
    const oldScrollTop = scrollTop; // 保存当前滚动位置

    const buffer = 5;
    if (scrollTop + clientHeight + buffer >= scrollHeight) {
      console.log('加载更多数据');
      if (params.value.paginator.curr_page < totalPages.value && !loadingRef.value) {
        params.value.paginator.curr_page += 1;
        loadingRef.value = true;
        const { data, extra } = await FetchManage(field.app_name, field.model_name, params.value);
        // optionsRef.value = [
        //   ...optionsRef.value,
        //   ...data.map((item: any) => ({ label: item.label, value: item.value.id })),
        // ];
        const addOptions = data.map((item: any) => ({ label: item.label, value: item.value.id }));
        optionsRef.value.push(...addOptions);
        totalPages.value = extra.paginator.page_cnt;
        loadingRef.value = false;
        // 在数据加载完成后恢复滚动位置
        requestAnimationFrame(() => {
          target.scrollTop = oldScrollTop;
        });
      }
    }
  }, 300);

  return {
    field,
    component: 'NSelect',
    loading: loadingRef,
    componentProps: {
      // value: selectedValue,
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
      style: field['style'] || {
        width: '320px',
      },
      onFocus: async () => {
        // debouncedSearch(searchStr.value);
      },
      onSearch: (query: string) => {
        // 使用防抖搜索函数
        searchStr.value = query;
        debouncedSearch(query);
      },
      onScroll: debouncedScroll,
    },
  };
}

export function createFormRules(fieldsInfo: any) {
  const rules = {};
  for (const field_name in fieldsInfo) {
    const field = fieldsInfo[field_name];
    const fieldRules: Recordable = [];
    if (field.is_required) {
      fieldRules.push({
        required: true,
        message: `${field.ud_name || field.field_name} 不能为空`,
        trigger: ['blur', 'input', 'change'],
        validator: (rule: any, value: string | null | undefined) => {
          const isValid = value !== null && value !== undefined && value !== '';
          return isValid;
        },
      });
    }
    switch (field.field_type) {
      case 'CharField':
        // 字符串字段
        fieldRules.push({
          type: 'string',
          message: `${field.ud_name || field.field_name} 必须是字符串`,
          trigger: ['blur', 'input'],
        });
        break;

      case 'JSONField':
        // JSON字段
        fieldRules.push({
          validator: (rule, value) => {
            if (typeof value === 'string' && !isNaN(Number(value))) {
              return false;
            }
            if (value === null || value === undefined || value === '') return true;
            try {
              if (typeof value === 'string') {
                JSON.parse(value);
              } else if (typeof value === 'object') {
                JSON.stringify(value);
              }
              return true;
            } catch (e) {
              return false;
            }
          },
          message: `${field.ud_name || field.field_name} 必须是有效的JSON`,
          trigger: ['blur', 'input', 'change'],
        });
        break;
      case 'FloatField':
        // 浮点数字段
        fieldRules.push({
          type: 'number',
          message: `${field.ud_name || field.field_name} 必须是数字`,
          trigger: ['blur', 'input'],
        });
        break;
    }
    // 如果有规则，则添加到规则对象中
    if (fieldRules.length > 0) {
      rules[field_name] = fieldRules;
    }
  }
  // console.log('@@@rules', rules);
  return rules;
}
