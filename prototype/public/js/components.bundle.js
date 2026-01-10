import { mountVue, unmountVue } from "./vue_helper.js";

frappe.provide("tahp.ui");
tahp.ui.mountVue = mountVue;
tahp.ui.unmountVue = unmountVue;

function createVueWrapper(name, component) {
  class VueWrapper {
    constructor({ wrapper, ...props }) {
      this.wrapper = wrapper;
      const mounted = mountVue(component, props, this.wrapper);

      this.app = mounted.app;
      this.vm = mounted.vm || mounted;

      Object.assign(this, this.vm);
    }

    destroy() {
      unmountVue(this.app || this.vm);
    }
  }

  tahp.ui[name + "Component"] = VueWrapper;
}

// createVueWrapper("TrackingProduction", TrackingProduction)
// 	const facenet_wrapper_html = `<div class="facenet-view">Anh Lộc chẻ châu</div>`;
// 	this.$frappe_list.html(facenet_wrapper_html);
// 	this.wrapper = this.$frappe_list.find('.facenet-view');
// 	this.component = new superproject.ui.BaseLayoutComponent({
// 		wrapper: this.wrapper[0],
// 		hide_tree: this.hide_tree,
// 		hide_flex: this.hide_flex,
// 		doctype: this.doctype,
// }