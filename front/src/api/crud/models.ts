import { Alova } from '@/utils/http/alova';
import { preurl } from '@/utils/prefixUrl';

/**
 * @description: 获取所有被允许的模型信息
 */
export function GetAllModelsInfo() {
  return Alova.Get<InResult>(
    // 组装请求
    preurl('/udadmin/get_all_models_info'),
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}
/**
 * @description: 获取模型字段信息
 */
export function GetAllowModelInfo(params) {
  return Alova.Post<InResult>(
    // 组装请求
    preurl('/udadmin/get_allow_model_info'),
    params,
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}
/**
 * @description: 获取字段distinct值
 */
export function GetFieldDistinctValues(params) {
  return Alova.Post<InResult>(
    // 组装请求
    preurl('/udadmin/get_filter_fields_distinct_values'),
    params,
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}

/**
 * @description: 获取字段distinct值
 */
export function GetModelItemList(app_name: string, model_name: string, params: any) {
  return Alova.Post<InResult>(
    // 组装请求
    preurl(`/${app_name}/models/${model_name}/list`),
    params,
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}
/**
 * @description: 根据id 删除记录
 */
export function GetModelItem(app_name: string, model_name: string, id: string | number) {
  return Alova.Get<InResult>(
    // 组装请求
    preurl(`/${app_name}/models/${model_name}/${id}`),
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}
/**
 * @description: 根据id 删除记录
 */
export function DeleteModelItem(app_name: string, model_name: string, id: string | number) {
  return Alova.Delete<InResult>(
    // 组装请求
    preurl(`/${app_name}/models/${model_name}/${id}`),
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}
/**
 * @description: 更新记录
 */
export function UpdateModelItem(
  app_name: string,
  model_name: string,
  id: string | number,
  params: Record<string, any>
) {
  return Alova.Put<InResult>(
    // 组装请求
    preurl(`/${app_name}/models/${model_name}/${id}`),
    params,
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}

/**
 * @description: 创建记录
 */
export function CreateModelItem(app_name: string, model_name: string, params: Record<string, any>) {
  return Alova.Post<InResult>(
    // 组装请求
    preurl(`/${app_name}/models/${model_name}`),
    params,
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}

/**
 * @description: 创建记录
 */
export function FetchManage(app_name: string, model_name: string, params: Record<string, any>) {
  return Alova.Post<InResult>(
    // 组装请求
    preurl(`/${app_name}/models/${model_name}/fetch_manage`),
    params,
    {
      meta: {
        isReturnNativeResponse: true,
      },
    }
  );
}
