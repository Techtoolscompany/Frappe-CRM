import frappe
from frappe import _
from frappe.utils import getdate, add_days, nowdate

def get_notification_config():
    """
    Return notification configuration for the Church Management module
    """
    return {
        "for_doctype": {
            "Church Member": {
                "birthday_today": {
                    "message": _("Birthday Today: {0}"),
                    "document_type": "Church Member"
                }
            },
            "Church Service": {
                "tomorrow": {
                    "message": _("Service Tomorrow: {0}"),
                    "document_type": "Church Service"
                }
            },
            "Church Event": {
                "registration_closing": {
                    "message": _("Event Registration Closing: {0}"),
                    "document_type": "Church Event"
                }
            },
            "Family Unit": {
                "pastoral_care": {
                    "message": _("Family Needs Pastoral Care: {0}"),
                    "document_type": "Family Unit"
                }
            }
        }
    }

def get_birthdays_today():
    """Get members with birthdays today"""
    today = getdate()
    return frappe.db.sql("""
        SELECT name, first_name, last_name, email, phone, family_unit
        FROM `tabChurch Member`
        WHERE DATE_FORMAT(date_of_birth, '%m-%d') = %s
        AND status = 'Active'
    """, (f"{today.month:02d}-{today.day:02d}"), as_dict=1)

def get_upcoming_services():
    """Get services scheduled for tomorrow"""
    tomorrow = add_days(nowdate(), 1)
    return frappe.get_all("Church Service",
        filters={
            "date": tomorrow,
            "status": "Scheduled"
        },
        fields=["name", "service_type", "start_time"]
    )

def get_events_registration_closing():
    """Get events with registration closing soon"""
    soon = add_days(nowdate(), 3)  # 3 days warning
    return frappe.get_all("Church Event",
        filters={
            "registration_deadline": ["between", [nowdate(), soon]],
            "status": ["in", ["Planning", "Registration Open"]]
        },
        fields=["name", "event_name", "registration_deadline"]
    )

def get_pastoral_care_needs():
    """Get families needing pastoral care"""
    return frappe.get_all("Family Unit",
        filters={
            "special_pastoral_care": 1
        },
        fields=["name", "family_name", "primary_contact"]
    )

def send_birthday_notifications():
    """Send birthday notifications to pastors and family members"""
    if not frappe.db.get_single_value("Church Settings", "enable_birthday_notifications"):
        return

    birthdays = get_birthdays_today()
    if not birthdays:
        return

    # Get pastors and admins to notify
    recipients = get_notification_recipients()

    for member in birthdays:
        # Get family members
        family_members = []
        if member.family_unit:
            family_members = frappe.get_all("Church Member",
                filters={
                    "family_unit": member.family_unit,
                    "name": ["!=", member.name],
                    "status": "Active"
                },
                fields=["email"]
            )

        # Combine all recipients
        all_recipients = recipients + [m.email for m in family_members if m.email]
        
        if all_recipients:
            frappe.sendmail(
                recipients=list(set(all_recipients)),
                template="Birthday Reminder",
                args={
                    "member_name": f"{member.first_name} {member.last_name}",
                    "birthday_date": getdate().strftime("%B %d"),
                    "church_name": frappe.db.get_single_value("Church Settings", "church_name")
                },
                subject=f"Birthday Reminder: {member.first_name} {member.last_name}"
            )

def send_service_reminders():
    """Send service reminders to relevant members"""
    if not frappe.db.get_single_value("Church Settings", "enable_service_reminders"):
        return

    services = get_upcoming_services()
    if not services:
        return

    for service in services:
        # Get members who usually attend this service time
        members = frappe.get_all("Church Member",
            filters={
                "status": "Active"
            },
            fields=["email", "first_name", "last_name"]
        )

        for member in members:
            if member.email:
                frappe.sendmail(
                    recipients=[member.email],
                    template="Service Reminder",
                    args={
                        "recipient_name": f"{member.first_name} {member.last_name}",
                        "service_title": service.service_type,
                        "service_date": service.date,
                        "service_time": service.start_time,
                        "church_name": frappe.db.get_single_value("Church Settings", "church_name")
                    },
                    subject=f"Service Reminder: {service.service_type}"
                )

def get_notification_recipients():
    """Get list of users who should receive notifications"""
    recipients = []
    
    # Get Church Pastors
    pastors = frappe.get_all("User",
        filters={
            "enabled": 1,
            "role": "Church Pastor"
        },
        fields=["email"]
    )
    recipients.extend([p.email for p in pastors if p.email])
    
    # Get Church Administrators
    admins = frappe.get_all("User",
        filters={
            "enabled": 1,
            "role": "Church Administrator"
        },
        fields=["email"]
    )
    recipients.extend([a.email for a in admins if a.email])
    
    return list(set(recipients))  # Remove duplicates

def create_pastoral_care_alerts():
    """Create alerts for families needing pastoral care"""
    families = get_pastoral_care_needs()
    
    for family in families:
        # Create a todo for pastors
        if not frappe.db.exists("ToDo", {
            "reference_type": "Family Unit",
            "reference_name": family.name,
            "status": "Open"
        }):
            frappe.get_doc({
                "doctype": "ToDo",
                "status": "Open",
                "priority": "High",
                "description": f"Pastoral Care Needed: {family.family_name}",
                "reference_type": "Family Unit",
                "reference_name": family.name,
                "role": "Church Pastor"
            }).insert(ignore_permissions=True)
