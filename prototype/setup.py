import frappe
import os
import json

def setup_website():
    logo_url = "/assets/prototype/images/facenet.png"
    logo_white_url = "/assets/prototype/images/facenet_white.png"

    frappe.db.set_value("Website Settings", "Website Settings", "brand_html", f"<img src='{logo_url}' height='30px'>")
    frappe.db.set_value("Website Settings", "Website Settings", "favicon", logo_white_url)
    frappe.db.set_value("Website Settings", "Website Settings", "app_logo", logo_white_url)
    frappe.db.set_value("Website Settings", "Website Settings", "splash_image", logo_url)
    frappe.db.set_value("Website Settings", "Website Settings", "app_name", "FaceNet Prototype")
    frappe.db.commit()

    print("✅ Cài đặt logo & tên app và ngôn ngữ thành công.")

def cleanup_custom():
    app_path = frappe.get_app_path("prototype")
    custom_path = os.path.join(app_path,"prototype","custom")
    if not os.path.isdir(custom_path):
        frappe.logger().info("No custom directory found, skipping cleanup_custom")
        return
    result = dict()
    for row in os.listdir(custom_path):
        dir = os.path.join(custom_path, row)
        with open(dir) as file:
            custom_data = json.load(file)
            dt = custom_data["doctype"]
            result[dt] = []
            for row in custom_data["custom_fields"]:
                result[dt].append(row["fieldname"])
    
    db_custom_fields = frappe.db.get_all(
        "Custom Field",
        fields=["name", "dt", "fieldname"]
    )
    for field in db_custom_fields:
        dt = field["dt"]
        fname = field["fieldname"]

        if dt in result and fname not in result[dt] and fname != "workflow_state":
            print(f"Deleting unused Custom Field: {dt}.{fname}")
            frappe.delete_doc("Custom Field", field["name"], force=1)

