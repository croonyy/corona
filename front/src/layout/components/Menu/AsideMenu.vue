<template>
  <NMenu
    :options="menus"
    :inverted="inverted"
    :mode="mode"
    :collapsed="collapsed"
    :collapsed-width="40"
    :collapsed-icon-size="20"
    :indent="24"
    :expanded-keys="openKeys"
    :value="getSelectedKeys"
    @update:value="clickMenuItem"
    @update:expanded-keys="menuExpanded"
  />
</template>

<script lang="ts">
  import {
    defineComponent,
    ref,
    onMounted,
    reactive,
    computed,
    watch,
    toRefs,
    unref,
    toRaw,
    onBeforeMount,
  } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useAsyncRouteStore } from '@/store/modules/asyncRoute';
  import { generatorMenu, generatorMenuMix } from '@/utils';
  import { useProjectSettingStore } from '@/store/modules/projectSetting';
  import { useProjectSetting } from '@/hooks/setting/useProjectSetting';
  import { getIcon } from '@/utils/getIconByName';
  // import { GetAllModelsInfo } from '@/api/crud/models';
  import { useCrudMenu } from '@/store/modules/crudMenu';
  import { UD_MENU, CRUD_LIST, CRUD_EDIT, CRUD_CREATE } from '@/store/consts';
  // import { storage } from '@/utils/Storage';
  // import {
  //   ACCESS_TOKEN,
  //   REFRESH_TOKEN,
  //   // CURRENT_USER,
  //   // IS_SCREENLOCKED,
  // } from '@/store/mutation-types';
  // import { useUser } from '@/store/modules/user';

  // import { MenuOption } from 'naive-ui';
  // import { Layout } from '@/router/constant';

  export default defineComponent({
    name: 'AppMenu',
    components: {},
    props: {
      mode: {
        // 菜单模式
        type: String,
        default: 'vertical',
      },
      collapsed: {
        // 侧边栏菜单是否收起
        type: Boolean,
      },
      //位置
      location: {
        type: String,
        default: 'left',
      },
    },
    emits: ['update:collapsed', 'clickMenuItem'],
    setup(props, { emit }) {
      // 当前路由
      const currentRoute = useRoute();
      const router = useRouter();
      const asyncRouteStore = useAsyncRouteStore();
      const settingStore = useProjectSettingStore();
      // const userStore = useUser();
      const menus = ref<any[]>([]);
      const selectedKeys = ref<string>(currentRoute.name as string);
      const headerMenuSelectKey = ref<string>('');
      let crud_menus = reactive({}); // crud菜单

      const { navMode } = useProjectSetting();

      // 获取当前打开的子菜单
      const matched = currentRoute.matched;
      // console.log('@@@', matched);

      const getOpenKeys = matched && matched.length ? matched.map((item) => item.name) : [];
      // console.log('@@@', getOpenKeys);

      const state = reactive({
        openKeys: getOpenKeys,
      });

      const inverted = computed(() => {
        return ['dark', 'header-dark'].includes(settingStore.navTheme);
      });

      const getSelectedKeys = computed(() => {
        let location = props.location;
        return location === 'left' || (location === 'header' && unref(navMode) === 'horizontal')
          ? unref(selectedKeys)
          : unref(headerMenuSelectKey);
      });

      // 监听分割菜单
      watch(
        () => settingStore.menuSetting.mixMenu,
        () => {
          updateMenu();
          if (props.collapsed) {
            // 代码的作用是：子组件在某些条件下改变自身的折叠状态，并将这个变化通知父组件，从而实现父子组件之间的状态同步。
            emit('update:collapsed', !props.collapsed);
          }
        }
      );

      // 监听菜单收缩状态
      // watch(
      //   () => props.collapsed,
      //   (newVal) => {
      //   }
      // );

      // 跟随页面路由变化，切换菜单选中状态
      watch(
        () => currentRoute.fullPath,
        () => {
          updateMenu();
        }
      );
      const CrudRoutes = [UD_MENU, CRUD_LIST, CRUD_EDIT, CRUD_CREATE];
      function updateSelectedKeys() {
        if (CrudRoutes.includes(currentRoute.meta?.type as string)) {
          const app_name = currentRoute.params.app_name;
          const model_name = currentRoute.params.model_name;
          // 自己添加的菜单需要自定义菜单项的打开状态和选中状态
          // 打开状态openKeys ， 选中状态selectedKeys
          const ud_app_name = toRaw(crud_menus)['all_models'][`${app_name}:${model_name}`].ud_app;
          state.openKeys = [`crud_list_${ud_app_name}`, `crud_list_${ud_app_name}_${model_name}`];
          // 选中状态
          selectedKeys.value = `crud_list_${ud_app_name}_${model_name}`;
        } else {
          const matched = currentRoute.matched;
          state.openKeys = matched.map((item) => item.name);
          const activeMenu: string = (currentRoute.meta?.activeMenu as string) || '';
          selectedKeys.value = activeMenu ? (activeMenu as string) : (currentRoute.name as string);
        }
        // console.log('@@@state.openKeys', state.openKeys);
        // console.log('@@@selectedKeys', selectedKeys.value);
      }

      function updateMenu() {
        // console.log('updateMenu');
        if (!settingStore.menuSetting.mixMenu) {
          // console.log('is not mixMenu');
          // console.log('getMenus', asyncRouteStore.getMenus);
          menus.value = generatorMenu(asyncRouteStore.getMenus);
        } else {
          // console.log('is mixMenu');
          //混合菜单
          const firstRouteName: string = (currentRoute.matched[0].name as string) || '';
          menus.value = generatorMenuMix(asyncRouteStore.getMenus, firstRouteName, props.location);
          // menus.value.push(
          //   generatorMenuMix(asyncRouteStore.getMenus, firstRouteName, props.location)
          // );
          const activeMenu: string = currentRoute?.matched[0].meta?.activeMenu as string;
          headerMenuSelectKey.value = (activeMenu ? activeMenu : firstRouteName) || '';
        }
        pushCrudMenu(crud_menus);
        // console.log('@@@menus', menus.value);
        updateSelectedKeys();
      }

      // 点击菜单
      function clickMenuItem(key: string, item: any) {
        // console.log('@@@clickMenuItem', toRaw(item));
        // 自己添加的菜单项会添加type字段，用type字段来判断用自己的点击逻辑，还是用原本的点击逻辑
        if (item?.type === CRUD_LIST) {
          router.push(item?.path);
          // console.log('clickMenuItem', key);
        } else {
          // console.log(crud_menus.value);
          if (/http(s)?:/.test(key)) {
            window.open(key);
          } else {
            router.push({ name: key });
          }
        }
        // emit('clickMenuItem' as any, key);
      }

      //展开菜单
      function menuExpanded(openKeys: string[]) {
        // console.log('menuExpanded', openKeys);
        if (!openKeys) return;
        const latestOpenKey = openKeys.find((key) => state.openKeys.indexOf(key) === -1);
        const isExistChildren = findChildrenLen(latestOpenKey as string);
        state.openKeys = isExistChildren ? (latestOpenKey ? [latestOpenKey] : []) : openKeys;
      }

      //查找是否存在子路由
      function findChildrenLen(key: string) {
        if (!key) return false;
        const subRouteChildren: string[] = [];
        for (const { children, key } of unref(menus)) {
          if (children && children.length) {
            subRouteChildren.push(key as string);
          }
        }
        return subRouteChildren.includes(key);
      }

      function pushCrudMenu(data: any) {
        let addmenu = {}; // 添加的菜单
        const models = data?.all_models || {};
        for (const key in models) {
          const model = models[key];
          const app_name = model.ud_app || model.app_name;
          // 判断app_name是否存在于menus的keys中
          if (!(app_name in addmenu)) {
            addmenu[app_name] = {
              children: [],
              icon: getIcon(model['app_icon'] || 'antd:TagsFilled'),
              key: `crud_list_${app_name}`,
              label: model.name || app_name,
              meta: {},
              name: model.name || app_name,
              path: model.name || app_name,
              title: model.app_menu_name || app_name,
              type: CRUD_LIST,
            };
          }
          const child = {
            key: `crud_list_${app_name}_${model.model_name}`,
            label: model.model_menu_name || model.model_name,
            meta: {},
            name: `${model.app}_${model.model_name}`,
            path: `/crud/list/${model.app}/${model.model_name}`,
            title: model.model_menu_name || model.model_name,
            type: CRUD_LIST,
          };
          addmenu[app_name].children.push(child);
        }
        for (const key in addmenu) {
          menus.value.push(addmenu[key]);
        }
      }
      const crudMenuStore = useCrudMenu();

      onMounted(async () => {
        await crudMenuStore.initCrudMenu();
        crud_menus = crudMenuStore.getCrudMenu;
        updateMenu();
        console.log('@@@router.getRoutes()', router.getRoutes());
      });

      onBeforeMount(async () => {
        // console.log('@@@onBeforeMount');
      });

      return {
        ...toRefs(state),
        inverted,
        menus,
        selectedKeys,
        headerMenuSelectKey,
        getSelectedKeys,
        clickMenuItem,
        menuExpanded,
      };
    },
  });
</script>
