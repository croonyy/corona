// 定义基础的过滤条件类型
interface FilterCondition {
  field: string;
  symbol: string;
  value: any;
}

// 定义递归的过滤器组类型
type FilterGroup = [] | ['and' | 'or', ...(FilterCondition | FilterGroup)[]];

type FilterElement = [] | FilterCondition | FilterGroup;

// 组合类型
// type Filter = FilterGroup | FilterCondition;

interface Paginator {
  curr_page: number;
  page_size: number;
  order_by: any[]; // 或者更具体的类型，如 string[] 或 Array<{field: string, direction: 'asc' | 'desc'}>
  filters: any[]; // 根据实际需求替换为更具体的类型
}

interface FatchManageParams {
  action: string; // 根据实际可能的 action 值扩展
  field_name: string; // 假设 field.field_name 是 string 类型
  label: boolean;
  id?: number | string; // 根据 id 的实际类型
  paginator: Paginator;
  m2m_ids: Recordable; // 根据 m2m_ids 的实际内容类型
}
