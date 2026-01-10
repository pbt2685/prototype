/**
 * Thêm nút "Fast Export" cho Customize Form
 * - Chỉ hiển thị ở chế độ developer
 * - Xuất nhanh customize form này vào trong Custom App
 * + Module: "Tahp"
 * + sync_on_migrate: true
 * + with_permissions: true
 */

frappe.ui.form.on('Customize Form', {
    refresh(frm) {
        if (frappe.boot.developer_mode) {
            frm.add_custom_button(
                __("Fast Export"),
                function () {
                    frappe.call({
                        method: "frappe.modules.utils.export_customizations",
                        args: {
                            doctype: frm.doc.doc_type,
                            module: "Tahp",
                            sync_on_migrate: 1,
                            with_permissions: 1,
                        },
                        callback: () => {}
                    });
                }
            );
        }
    }
});
