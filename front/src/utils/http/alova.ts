import { createAlova } from 'alova';
import VueHook from 'alova/vue';
import adapterFetch from 'alova/fetch';
import { createAlovaMockAdapter } from '@alova/mock';
// import { isString } from 'lodash-es';
import mocks from './mocks';
import { useUser } from '@/store/modules/user';
// import { storage } from '@/utils/Storage';
import { useGlobSetting } from '@/hooks/setting';
// import { isUrl } from '@/utils';
// import { ACCESS_TOKEN } from '@/store/mutation-types';
// import { createClientTokenAuthentication } from 'alova/client';
import { createServerTokenAuthentication } from 'alova/client';

// // 绑定基于客户端的身份认证的拦截器
// const { onAuthRequired, onResponseRefreshToken } = createClientTokenAuthentication({
//   // 这里也可以做login拦截设置localstorage的token，refreshtoken,因为在userStore中已经做了，所以这里就不需要了
//   // login:(response, method)=>{
//   //   console.log('login interrupter');
//   //   // localStorage.setItem('token', response.token);
//   //   // localStorage.setItem('refresh_token', response.refresh_token);
//   // },
//   assignToken: (method) => {
//     const token = useUser().getToken;
//     // 添加 token 到请求头
//     if (!method.meta?.ignoreToken && token) {
//       method.config.headers['token'] = token;
//       // method.config.headers['authorization'] = `Bearer ${token}`; // 这里是使用Bearer Token模式
//       method.config.headers.Authorization = `Bearer ${token}`;
//     }
//   },
//   refreshToken: {
//     // 在请求前触发，将接收到method参数，并返回boolean表示token是否过期
//     // isExpired: (method) => {
//     isExpired: () => {
//       const access_token = storage.get(ACCESS_TOKEN);
//       if (access_token) {
//         return false;
//       } else {
//         return true;
//       }
//     },

//     // 当token过期时触发，在此函数中触发刷新token
//     // handler: async (method) => {
//     handler: async () => {
//       try {
//         await useUser().refreshToken();
//       } catch (error) {
//         // token刷新失败，跳转回登录页
//         location.href = '/login';
//         // 并抛出错误
//         throw error;
//       }
//     },
//   },
// });

// 绑定基于服务端的身份认证拦截器
const { onAuthRequired, onResponseRefreshToken } = createServerTokenAuthentication({
  visitorMeta: {
    // 这里可以设置是否是游客模式，如果是游客模式，则不进行token校验,比如refreshToken接口就不需要token校验
    // api 里面设置isVisitor: true  就是访客api，不需要token校验，也就是不执行assignToken方法
    isVisitor: true,
  },
  assignToken: (method) => {
    // console.log('alova@@@assignToken', method.url);
    const token = useUser().getToken;
    // 添加 token 到请求头
    if (!method.meta?.ignoreToken && token) {
      method.config.headers['token'] = token;
      // method.config.headers['authorization'] = `Bearer ${token}`; // 这里是使用Bearer Token模式
      method.config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log('alova@@@assignToken no token');
      // useUser().refreshToken();
    }
  },
  refreshTokenOnSuccess: {
    // isExpired: (response, method) => {
    isExpired: (response) => {
      return [401].includes(response.status);
    },

    // 当token过期时触发，在此函数中触发刷新token
    // todo 数据库user表清空的时候 会有一个无线重试的bug
    handler: async (method) => {
      console.log('alova@@@refreshTokenOnSuccess 服务端token过期,尝试refreshtoken');
      try {
        await useUser().refreshToken();
      } catch (error) {
        console.log('!!!', error);
        // token刷新失败，跳转回一个需要登录的页面（因为需要登录，而现在没登录，就会重定向到login），重定向会触发路由守卫的模态框
        const Modal = window['$dialog'];
        console.log('@@@handler', method);
        Modal?.warning({
          title: '错误',
          content: '登录凭证已失效，请重新登录!',
          positiveText: 'OK',
          closable: false,
          maskClosable: false,
          onPositiveClick: async () => {
            // router.push({ name: 'Login' });
            location.href = `/login`;
          },
        });

        // 并抛出错误
        throw error;
      }
    },
  },
});

const { useMock, apiUrl, loggerMock } = useGlobSetting();

const mockAdapter = createAlovaMockAdapter([...mocks], {
  // 全局控制是否启用mock接口，默认为true
  enable: useMock,

  // 非模拟请求适配器，用于未匹配mock接口时发送请求
  httpAdapter: adapterFetch(),

  // mock接口响应延迟，单位毫秒
  delay: 1000,

  // 自定义打印mock接口请求信息
  // mockRequestLogger: (res) => {
  //   loggerMock && console.log(`Mock Request ${res.url}`, res);
  // },
  mockRequestLogger: loggerMock,
  onMockError(error, currentMethod) {
    console.error('🚀 ~ onMockError ~ currentMethod:', currentMethod);
    console.error('🚀 ~ onMockError ~ error:', error);
  },
});

export const Alova = createAlova({
  baseURL: apiUrl,
  statesHook: VueHook,
  timeout: 10000, // 请求超时时间，单位毫秒
  // 关闭全局请求缓存
  cacheFor: null,
  // 全局缓存配置
  // cacheFor: {
  //   POST: {
  //     mode: 'memory',
  //     expire: 60 * 10 * 1000
  //   },
  //   GET: {
  //     mode: 'memory',
  //     expire: 60 * 10 * 1000
  //   },
  //   HEAD: 60 * 10 * 1000 // 统一设置HEAD请求的缓存模式
  // },
  // 在开发环境开启缓存命中日志
  cacheLogger: process.env.NODE_ENV === 'development',
  requestAdapter: mockAdapter,
  // @ts-ignore
  beforeRequest: onAuthRequired((method) => {
    console.log(`alova@@@beforeRequest:Alova[${method.type}]:${method.url}`);
    // const userStore = useUser();
    // const token = userStore.getToken;
  }),
  responded: onResponseRefreshToken(async (response, method) => {
    // console.log(`alova@@@responded:Alova[${method.type}]:${method.url}`);
    // @ts-ignore
    const Message = window.$message;
    // 处理不是json响应
    const res = response.json && (await response.json());
    if (!res) {
      console.log(`Alova[${method.type}]:${method.url} is not json response.`);
      console.log('@@@response', response);
      throw new Error(res.error); // 抛出错误，会触发onError钩子
    }
    // 处理非200状态码
    if (response.status >= 300) {
      console.log(`Alova请求[${method.type}]:${method.url} 失败 status:${response.status}`);
      console.log('@@@res', res);
      // Message.error(res.error);
      throw new Error(res.error); // 抛出错误，会触发onError钩子
    }
    // 是否返回原生响应头 比如：需要获取响应头时使用该属性
    if (method.meta?.isReturnNativeResponse) {
      return res;
    } else {
      const { data } = res;
      return data;
    }
    // 请根据自身情况修改数据结构
    // const { code, msg, error, extra, data } = res;
  }),
});

// 项目，多个不同 api 地址，可导出多个实例
// export const AlovaTwo = createAlova({
//   baseURL: 'http://localhost:9001',
// });
