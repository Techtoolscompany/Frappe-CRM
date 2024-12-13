app_name = "church_management"
app_title = "Church Management"
app_publisher = "Your Organization"
app_description = "A comprehensive church management system"
app_email = "your.email@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/church_management/css/church_management.css"
# app_include_js = "/assets/church_management/js/church_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/church_management/css/church_management.css"
# web_include_js = "/assets/church_management/js/church_management.js"

# Installation
# ------------

before_install = "church_management.setup.before_install"
after_install = "church_management.setup.after_install"

# Desk Notifications
# ------------------
notification_config = "church_management.notifications.get_notification_config"

# Permissions
# -----------
has_permission = {
    "Church Member": "church_management.permissions.has_member_permission",
    "Family Unit": "church_management.permissions.has_family_permission",
}

# Document Events
# --------------
doc_events = {
    "Church Member": {
        "after_insert": "church_management.church_management.doctype.church_member.church_member.after_insert",
        "on_update": "church_management.church_management.doctype.church_member.church_member.on_update",
        "validate": "church_management.church_management.doctype.church_member.church_member.validate"
    },
    "Family Unit": {
        "validate": "church_management.church_management.doctype.family_unit.family_unit.validate",
        "on_update": "church_management.church_management.doctype.family_unit.family_unit.on_update"
    }
}

# Scheduled Tasks
# --------------
scheduler_events = {
    "daily": [
        "church_management.tasks.daily.send_birthday_notifications",
        "church_management.tasks.daily.send_service_reminders",
        "church_management.tasks.daily.check_pastoral_care_needs"
    ],
    "weekly": [
        "church_management.tasks.weekly.send_attendance_report",
        "church_management.tasks.weekly.check_asset_maintenance"
    ],
    "monthly": [
        "church_management.tasks.monthly.send_donation_summary",
        "church_management.tasks.monthly.generate_ministry_report"
    ]
}

# Custom Roles
# -----------
custom_roles = [
    {
        "name": "Church Pastor",
        "desk_access": 1,
        "is_custom": 1,
        "module": "Church Management"
    },
    {
        "name": "Church Administrator",
        "desk_access": 1,
        "is_custom": 1,
        "module": "Church Management"
    }
]

# DocType Class
# ------------
override_doctype_class = {
    "Church Member": "church_management.church_management.doctype.church_member.church_member.ChurchMember",
    "Family Unit": "church_management.church_management.doctype.family_unit.family_unit.FamilyUnit"
}

# Fixtures
# --------
fixtures = [
    {
        "dt": "Role",
        "filters": [["name", "in", ["Church Pastor", "Church Administrator"]]]
    },
    {
        "dt": "Custom Role",
        "filters": [["module", "=", "Church Management"]]
    },
    {
        "dt": "Workspace",
        "filters": [["module", "=", "Church Management"]]
    }
]

# Reports
# -------
standard_reports = {
    "Family Tags Analysis": "church_management.church_management.report.family_tags_analysis.family_tags_analysis"
}

# Jinja Environment
# ----------------
jinja = {
    "methods": [
        "church_management.utils.jinja_methods"
    ],
    "filters": [
        "church_management.utils.jinja_filters"
    ]
}

# Web Routes
# ----------
website_route_rules = [
    {"from_route": "/church/*", "to_route": "church_management"},
]

# Portal Menu Items
# ----------------
portal_menu_items = [
    {"title": "Church Events", "route": "/church/events", "role": "Guest"},
    {"title": "Small Groups", "route": "/church/groups", "role": "Guest"}
]
