import type { RouteRecordRaw } from 'vue-router';
import { isNavigationFailure, Router } from 'vue-router';
import { useUser } from '@/store/modules/user';
import { useAsyncRoute } from '@/store/modules/asyncRoute';
import { ACCESS_TOKEN } from '@/store/mutation-types';
import { storage } from '@/utils/Storage';
import { PageEnum } from '@/enums/pageEnum';
import { ErrorPageRoute } from '@/router/base';

// const whitePathList = [PageEnum.BASE_LOGIN, '/']; // no redirect whitelist
const whitePathList = [PageEnum.BASE_LOGIN, '/crud/test', '/']; // no redirect whitelist

export function createRouterGuards(router: Router) {
  const userStore = useUser();
  const asyncRouteStore = useAsyncRoute();

  router.beforeEach(async (to, from, next) => {
    // console.log('@@@guards router_from', from);
    // console.log('@@@guards router_to', to);
    console.log(`@@@guards [${from.path}] → [${to.path}]`);
    const Loading = window['$loading'] || null;
    Loading && Loading.start();
    //登录的时候如果是一个不存在的redirect 则跳到base_home
    if (from.path === PageEnum.BASE_LOGIN && to.name === 'errorPage') {
      console.log('@@@guards login 跳转错误页面', to.path);
      next(PageEnum.BASE_HOME);
      return;
    }

    // 白名单直接跳转,需要保证路由添加完成，否则会白屏，login是静态路由，所以可以直接白名单，如果是动态路由就会白屏
    if (whitePathList.includes(to.path as PageEnum)) {
      console.log('@@@guards 白名单直接跳转', to.path);
      next();
      return;
    }

    // 动态路由
    if (!asyncRouteStore.getIsDynamicRouteAdded) {
      const userInfo = await userStore.getInfo();
      const routes = await asyncRouteStore.generateRoutes(userInfo);
      // 动态添加可访问路由表
      routes.forEach((item: unknown) => {
        router.addRoute(item as unknown as RouteRecordRaw);
      });

      //添加404
      const isErrorPage = router.getRoutes().findIndex((item) => item.name === ErrorPageRoute.name);
      if (isErrorPage === -1) {
        router.addRoute(ErrorPageRoute as unknown as RouteRecordRaw);
      }
      asyncRouteStore.setDynamicRouteAdded(true);
      console.log('@@@guards 动态路由添加完成，重定向到to.path', to.path);
      // 动态路由添加完成，重定向到to.path（为了让动态路由携带路由的信息成为to参数）
      next({ ...to, replace: true });
      return;
    }
    // 动态路由添加之后重定向后，如果路由设置了ignoreAuth，不需要token则直接跳转
    if (to.meta.ignoreAuth) {
      console.log('@@@guards ignoreAuth 直接跳转：', to.path);
      next();
      return;
    }
    // 动态路由添加之后重定向后，需要token却没有token的情况
    if (!storage.get(ACCESS_TOKEN)) {
      const Modal = window['$dialog'];
      console.log('@@@guards no token');
      const redirectData: { path: string; replace: boolean; query?: Recordable<string> } = {
        path: PageEnum.BASE_LOGIN,
        replace: true,
      };
      if (to.path) {
        redirectData.query = {
          ...redirectData.query,
          redirect: to.path,
        };
      }
      try {
        await userStore.refreshToken();
      } catch (error) {
        console.log('@@@refreshToken error', error);
        Modal?.warning({
          title: '错误',
          content: '登录凭证已失效，请重新登录!',
          positiveText: 'OK',
          closable: false,
          maskClosable: false,
          // eslint-disable-next-line prettier/prettier
          onPositiveClick: async () => { },
        });
        next(redirectData);
        return;
      }
    }
    next();
    return;
  });

  router.afterEach((to, _, failure) => {
    // console.log('@@@afterEach  to', to);
    // console.log('@@@afterEach  failure', failure);
    document.title = (to?.meta?.title as string) || document.title;
    if (isNavigationFailure(failure)) {
      // console.log('failed navigation', failure);
    }
    const asyncRouteStore = useAsyncRoute();
    // 在这里设置需要缓存的组件名称
    const keepAliveComponents = asyncRouteStore.keepAliveComponents;
    const currentComName: any = to.matched.find((item) => item.name == to.name)?.name;
    if (currentComName && !keepAliveComponents.includes(currentComName) && to.meta?.keepAlive) {
      // 需要缓存的组件
      keepAliveComponents.push(currentComName);
    } else if (!to.meta?.keepAlive || to.name == 'Redirect') {
      // 不需要缓存的组件
      const index = asyncRouteStore.keepAliveComponents.findIndex((name) => name == currentComName);
      if (index != -1) {
        keepAliveComponents.splice(index, 1);
      }
    }
    // console.log('@@@guards setkeepAliveComponents', keepAliveComponents);
    asyncRouteStore.setKeepAliveComponents(keepAliveComponents);
    const Loading = window['$loading'] || null;
    Loading && Loading.finish();
  });

  router.onError((error) => {
    console.log(error, '路由错误');
  });
}
