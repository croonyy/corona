import { RouteRecordRaw } from 'vue-router';
import { Layout } from '@/router/constant';
import { getIcon } from '@/utils/getIconByName';
const IFrame = () => import('@/views/iframe/index.vue');

const routes: Array<RouteRecordRaw> = [
  {
    path: '/test',
    name: 'test',
    redirect: '/test/index',
    component: Layout,
    meta: {
      title: 'Test',
      icon: getIcon(''),
      // permissions: ['dashboard_console', 'dashboard_console', 'dashboard_workplace'],
      sort: 0,
    },
    children: [
      {
        path: 'index',
        name: 'test_index',
        meta: {
          title: 'index',
          // permissions: ['dashboard_console'],
          // affix: true, // 固定到导航栏
        },
        component: () => import('@/views/test/index.vue'),
      },
      {
        path: 'test_component',
        name: 'test_component',
        meta: {
          title: '组件',
          // permissions: ['dashboard_console'],
          // affix: true, // 固定到导航栏
        },
        component: () => import('@/views/test/test_component.vue'),
      },
      {
        path: 'docs',
        name: 'frame-docs',
        meta: {
          title: '项目文档(内嵌)',
          keepAlive: true,
          frameSrc: 'https://naive-ui-admin-docs.vercel.app',
        },
        component: IFrame,
      },
      {
        path: 'naive',
        name: 'frame-naive',
        meta: {
          title: 'NaiveUi(内嵌)',
          keepAlive: true,
          frameSrc: 'https://www.naiveui.com',
        },
        component: IFrame,
      },
      {
        path: 'guide',
        name: 'frame-guide',
        meta: {
          title: 'NaiveUi-guide(内嵌)',
          keepAlive: true,
          frameSrc: 'https://docs.naiveadmin.com/guide/',
        },
        component: IFrame,
      },
    ],
  },
];

export default routes;
