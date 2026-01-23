"""
Set user language to Vietnamese and update System Settings
"""
import frappe

def execute():
    """Set all users to Vietnamese and update system defaults"""
    
    # Update System Settings default language
    frappe.db.set_value("System Settings", None, "language", "vi")
    
    # Update all users to Vietnamese
    users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"})
    
    for user in users:
        frappe.db.set_value("User", user.name, "language", "vi")
        print(f"Set language to Vietnamese for user: {user.name}")
    
    frappe.db.commit()
    print("✓ Set Vietnamese as default language for system and all users")
