import { createApp } from "vue";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";

export function mountVue(Component, props, wrapper) {
  const el = wrapper?.get ? wrapper.get(0) : wrapper;

  if (el.__vue_app__) {
    try {
      el.__vue_app__.app.unmount();
    } catch (e) {
      console.warn("Unmounting previous Vue app failed:", e);
    }
    el.innerHTML = "";
  }

  const app = createApp(Component, props);
  app.use(Antd);
  SetVueGlobals(app);

  const vm = app.mount(el);
  el.__vue_app__ = { app, vm, el };
  return { app, vm, el };
}

export function unmountVue(mountedApp) {
  if (!mountedApp) return;

  try {
    if (mountedApp.app) {
      mountedApp.app.unmount();
    }
    if (mountedApp.el) {
      mountedApp.el.innerHTML = "";
      delete mountedApp.el.__vue_app__;
    }
  } catch (e) {
    console.warn("Error unmounting Vue app:", e);
  }
}
