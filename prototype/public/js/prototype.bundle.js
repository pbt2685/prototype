import { mountVue, unmountVue } from "./vue_helper.js";
import "./components.bundle.js"

frappe.provide("tahp.vue");
tahp.vue.mountVue = mountVue;
tahp.vue.unmountVue = unmountVue;