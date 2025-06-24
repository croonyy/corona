import { h } from 'vue';
import { NIcon } from 'naive-ui';
import {
  NumberOutlined,
  FieldBinaryOutlined,
  CheckCircleOutlined,
  FieldNumberOutlined,
  FieldStringOutlined,
  CalendarOutlined,
  FieldTimeOutlined,
  FileTextOutlined,
  // LinkOutlined,
  // PictureOutlined,
  // FileOutlined,
  CodeOutlined,
  IdcardOutlined,
  // DatabaseOutlined,
  ClockCircleOutlined,
  // GlobalOutlined,
  // FileSearchOutlined,
  // TagOutlined,
  // ApiOutlined,
  FileUnknownOutlined,
  UnorderedListOutlined,
  DatabaseOutlined,
} from '@vicons/antd';

export const fieldTypeIcons = {
  BigIntField: NumberOutlined,
  BinaryField: FieldBinaryOutlined,
  BooleanField: CheckCircleOutlined,
  CharEnumFieldInstance: UnorderedListOutlined,
  CharField: FieldStringOutlined,
  DateField: CalendarOutlined,
  DatetimeField: FieldTimeOutlined,
  DecimalField: FieldNumberOutlined,
  FloatField: FieldNumberOutlined,
  IntEnumFieldInstance: UnorderedListOutlined,
  IntField: NumberOutlined,
  JSONField: CodeOutlined,
  SmallIntField: NumberOutlined,
  TextField: FileTextOutlined,
  TimeDeltaField: ClockCircleOutlined,
  TimeField: FieldTimeOutlined,
  UUIDField: IdcardOutlined,
  OneToOneFieldInstance: DatabaseOutlined,
  ForeignKeyFieldInstance: DatabaseOutlined,
  Default: FileUnknownOutlined,
  // ManyToManyFieldInstance: 'NInput',
  // ForeignKeyFieldInstance: 'NInput',
};

export function renderIconTitle(field: any) {
  const IconComponent = fieldTypeIcons[field.field_type] || fieldTypeIcons.Default;
  return h('div', { style: 'display: flex; align-items: center;' }, [
    h(
      NIcon,
      { size: 16, style: 'margin-right: 5px;', title: field.field_type },
      { default: () => h(IconComponent, { style: 'color: #aaa;' }) }
    ),
    field.ud_name || field.field_name,
  ]);
}

export const columnRenderMap = {
  BooleanField: (field) => ({
    title: renderIconTitle(field),
    // title: item.field_name,
    key: field.field_name,
    resizable: true,
    // minWidth: 50,
    // maxWidth: 100,
    // ellipsis: {
    //   tooltip: true,
    // },
    render: (row) => (row[field.field_name] ? '是' : '否'),
  }),
  JSONField: (field) => ({
    title: renderIconTitle(field),
    key: field.field_name,
    // width: 100,
    resizable: true,
    render: (row) => JSON.stringify(row[field.field_name]),
  }),
  OneToOneFieldInstance: (field) => ({
    title: renderIconTitle(field),
    key: field.field_name,
    // width: 100,
    resizable: true,
    render: (row) => row[field.source_field],
  }),
  ForeignKeyFieldInstance: (field) => ({
    title: renderIconTitle(field),
    key: field.field_name,
    // width: 100,
    resizable: true,
    render: (row) => row[field.source_field],
  }),
  default: (field) => ({
    title: renderIconTitle(field),
    key: field.field_name,
    // width: 50,
    resizable: true,
    // sorter: (row1, row2) => {
    //   const value1 = row1[item.field_name];
    //   const value2 = row2[item.field_name];
    //   if (typeof value1 === 'number' && typeof value2 === 'number') {
    //     return value1 - value2;
    //   }
    // },
  }),
};
