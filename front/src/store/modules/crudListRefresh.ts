import { defineStore } from 'pinia';
import { store } from '@/store';

export const useCrudRefreshStore = defineStore('crudRefresh', {
  state: () => ({
    refreshFlags: new Map<string, boolean>(), // key: "appName_modelName", value: boolean
  }),
  actions: {
    setRefreshFlag(appName: string, modelName: string) {
      const key = `${appName}_${modelName}`;
      this.refreshFlags.set(key, true);
    },
    getRefreshFlag(appName: string, modelName: string): boolean {
      const key = `${appName}_${modelName}`;
      return this.refreshFlags.get(key) || false;
    },
    clearRefreshFlag(appName: string, modelName: string) {
      const key = `${appName}_${modelName}`;
      this.refreshFlags.delete(key);
    },
  },
});

export function useCrudRefresh() {
  return useCrudRefreshStore(store);
}
