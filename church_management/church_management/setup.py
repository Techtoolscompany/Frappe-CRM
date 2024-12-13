import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def before_install():
    """Setup operations before installing the app"""
    create_roles()
    setup_permissions()

def after_install():
    """Setup operations after installing the app"""
    create_default_settings()
    setup_workspace()
    create_notification_templates()

def create_roles():
    """Create custom roles if they don't exist"""
    roles = ["Church Pastor", "Church Administrator"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            doc = frappe.new_doc("Role")
            doc.role_name = role
            doc.desk_access = 1
            doc.is_custom = 1
            doc.save()

def setup_permissions():
    """Setup default permissions for custom roles"""
    permissions_map = {
        "Church Pastor": [
            {
                "doctype": "Church Member",
                "permlevel": 0,
                "rights": ["read", "write", "create", "report", "export"]
            },
            {
                "doctype": "Family Unit",
                "permlevel": 0,
                "rights": ["read", "write", "create", "report", "export"]
            },
            {
                "doctype": "Church Service",
                "permlevel": 0,
                "rights": ["read", "write", "create", "cancel", "report"]
            }
        ],
        "Church Administrator": [
            {
                "doctype": "Church Member",
                "permlevel": 0,
                "rights": ["read", "write", "create", "delete", "report", "export"]
            },
            {
                "doctype": "Family Unit",
                "permlevel": 0,
                "rights": ["read", "write", "create", "delete", "report", "export"]
            },
            {
                "doctype": "Church Settings",
                "permlevel": 0,
                "rights": ["read", "write", "create", "report"]
            }
        ]
    }

    for role, permissions in permissions_map.items():
        for perm in permissions:
            if not frappe.db.exists("Custom DocPerm", {"role": role, "parent": perm["doctype"]}):
                doc = frappe.new_doc("Custom DocPerm")
                doc.role = role
                doc.parent = perm["doctype"]
                doc.permlevel = perm["permlevel"]
                for right in perm["rights"]:
                    setattr(doc, right, 1)
                doc.save()

def create_default_settings():
    """Create default Church Settings"""
    if not frappe.db.exists("Church Settings", "Church Settings"):
        doc = frappe.new_doc("Church Settings")
        doc.church_name = "Your Church Name"
        doc.default_service_duration = "02:00:00"
        doc.enable_birthday_notifications = 1
        doc.enable_service_reminders = 1
        doc.enable_offering_reports = 1
        doc.advance_reminder_days = 1
        doc.save()

def setup_workspace():
    """Setup default workspace configuration"""
    if not frappe.db.exists("Workspace", "Church Management"):
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "name": "Church Management",
            "label": "Church Management",
            "category": "Modules",
            "is_standard": 1,
            "public": 1
        })
        workspace.insert()

def create_notification_templates():
    """Create email notification templates"""
    templates = [
        {
            "name": "Birthday Reminder",
            "subject": "Birthday Reminder: {{ member_name }}",
            "response": """
Dear {{ recipient_name }},

This is a reminder that {{ member_name }} has an upcoming birthday on {{ birthday_date }}.

Best regards,
{{ church_name }}
            """
        },
        {
            "name": "Service Reminder",
            "subject": "Upcoming Service: {{ service_title }}",
            "response": """
Dear {{ recipient_name }},

This is a reminder about the upcoming service:

Service: {{ service_title }}
Date: {{ service_date }}
Time: {{ service_time }}

Best regards,
{{ church_name }}
            """
        }
    ]

    for template in templates:
        if not frappe.db.exists("Email Template", template["name"]):
            doc = frappe.new_doc("Email Template")
            doc.name = template["name"]
            doc.subject = template["subject"]
            doc.response = template["response"]
            doc.save()

def get_setup_stages():
    """Return setup stages for installation"""
    return [
        {
            "status": "Pending",
            "fail_msg": "Failed to create roles",
            "tasks": [
                {"fn": "church_management.setup.create_roles", "args": []},
                {"fn": "church_management.setup.setup_permissions", "args": []}
            ]
        },
        {
            "status": "Pending",
            "fail_msg": "Failed to create default settings",
            "tasks": [
                {"fn": "church_management.setup.create_default_settings", "args": []}
            ]
        },
        {
            "status": "Pending",
            "fail_msg": "Failed to setup workspace",
            "tasks": [
                {"fn": "church_management.setup.setup_workspace", "args": []},
                {"fn": "church_management.setup.create_notification_templates", "args": []}
            ]
        }
    ]
