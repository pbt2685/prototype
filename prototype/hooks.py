app_name = "prototype"
app_title = "Prototype"
app_publisher = "FaceNet"
app_description = "FaceNet"
app_email = "trunghieu.personal@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "prototype",
# 		"logo": "/assets/prototype/logo.png",
# 		"title": "Prototype",
# 		"route": "/prototype",
# 		"has_permission": "prototype.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

fixtures = [
    {"doctype": "Role", "filters": [["is_custom", "=", 1]]},
    {"dt": "Custom Field", "filters": [["fieldname", "=", "workflow_state"]]},
    {"doctype": "Workflow"},
    {"doctype": "Workflow State"},
    {"doctype": "Workflow Action Master"},
    {"doctype": "Workspace"},
    {"doctype": "Website Settings"},
    {"doctype": "System Settings"},
    {"doctype": "Role Profile"},
    {"doctype": "List View Settings"},
    {"doctype": "Letter Head"},
]

app_include_css = [
    "/assets/prototype/css/build.css",
    "/assets/prototype/css/desk.css",
    "/assets/prototype/css/custom.css",
    "/assets/prototype/css/report.css",
    "/assets/prototype/js/prototype/custom/datatable/style.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
]
# app_include_js = "/assets/prototype/js/prototype.js"
app_include_js = [
    "my_desk.bundle.js",
    "prototype.bundle.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/prototype/css/prototype.css"
web_include_css = [
    "/assets/prototype/css/web.css"
]

# include js, css files in header of desk.html
# app_include_css = "/assets/prototype/css/prototype.css"
# app_include_js = "/assets/prototype/js/prototype.js"

# include js, css files in header of web template
# web_include_css = "/assets/prototype/css/prototype.css"
# web_include_js = "/assets/prototype/js/prototype.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "prototype/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "prototype/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "prototype.utils.jinja_methods",
# 	"filters": "prototype.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "prototype.install.before_install"
# after_install = "prototype.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "prototype.uninstall.before_uninstall"
# after_uninstall = "prototype.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "prototype.utils.before_app_install"
# after_app_install = "prototype.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "prototype.utils.before_app_uninstall"
# after_app_uninstall = "prototype.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "prototype.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"prototype.tasks.all"
# 	],
# 	"daily": [
# 		"prototype.tasks.daily"
# 	],
# 	"hourly": [
# 		"prototype.tasks.hourly"
# 	],
# 	"weekly": [
# 		"prototype.tasks.weekly"
# 	],
# 	"monthly": [
# 		"prototype.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "prototype.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "prototype.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "prototype.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["prototype.utils.before_request"]
# after_request = ["prototype.utils.after_request"]

# Job Events
# ----------
# before_job = ["prototype.utils.before_job"]
# after_job = ["prototype.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"prototype.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

