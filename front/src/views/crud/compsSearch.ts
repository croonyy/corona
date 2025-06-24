// import { GetFieldDistinctValues } from '@/api/crud/models';
// // import type { SelectOption } from 'naive-ui';
// import { ref, reactive } from 'vue';
// import { SelectOption } from 'naive-ui';
// 搜索字段表单对应的key
export const search_component_key = '__search_value__';

export function SearchFieldComponent(fields: any[]) {
  const names = fields.map((field) => field.ud_name || field.field_name).join('、');
  const placeholder = `请输入关键字搜索以下字段${names}`;
  return {
    field: search_component_key,
    component: 'NInput',
    label: '搜索',
    // labelWidth: 'auto', // 让label宽度自适应
    // labelStyle: {
    //   width: '100%',
    //   textAlign: 'center',
    // },
    componentProps: {
      placeholder,
      title: placeholder,
      onInput: () => {
        // console.log('onInput', e);
      },
    },
  };
}
