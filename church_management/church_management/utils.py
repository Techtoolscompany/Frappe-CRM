import frappe
from frappe import _
from frappe.utils import (
    get_url, get_datetime, getdate, nowdate,
    fmt_money, format_datetime, format_date
)

def get_church_settings():
    """Get church settings with defaults"""
    settings = frappe.get_single("Church Settings")
    return {
        "church_name": settings.church_name or "Our Church",
        "contact_email": settings.contact_email,
        "contact_phone": settings.contact_phone,
        "default_currency": settings.default_currency or "USD",
        "enable_birthday_notifications": settings.enable_birthday_notifications,
        "enable_service_reminders": settings.enable_service_reminders,
        "enable_offering_reports": settings.enable_offering_reports,
        "advance_reminder_days": settings.advance_reminder_days or 1
    }

def format_currency(amount, currency=None):
    """Format currency with church's default currency"""
    if not currency:
        settings = get_church_settings()
        currency = settings.get("default_currency")
    return fmt_money(amount, currency=currency)

def get_email_template(template_name, context=None):
    """Get rendered email template with context"""
    if context is None:
        context = {}
    
    # Add church settings to context
    settings = get_church_settings()
    context.update(settings)
    
    # Add common template functions
    context.update({
        "get_url": get_url,
        "format_datetime": format_datetime,
        "format_date": format_date,
        "format_currency": format_currency
    })
    
    template = frappe.get_template(
        f"templates/emails/{template_name}.html"
    )
    return template.render(context)

def get_family_details(family_unit):
    """Get comprehensive family unit details"""
    family = frappe.get_doc("Family Unit", family_unit)
    
    # Get family members
    members = frappe.get_all("Church Member",
        filters={"family_unit": family_unit},
        fields=["name", "first_name", "last_name", "family_role", 
                "email", "phone", "family_primary_contact"]
    )
    
    # Get family tags
    tags = {}
    if family.family_tags:
        for tag in family.family_tags:
            if tag.tag_category not in tags:
                tags[tag.tag_category] = []
            tags[tag.tag_category].append(tag.tag_value)
    
    return {
        "family_name": family.family_name,
        "primary_contact": family.primary_contact,
        "contact_phone": family.contact_phone,
        "contact_email": family.contact_email,
        "address": family.address,
        "city": family.city,
        "state": family.state,
        "country": family.country,
        "members": members,
        "tags": tags,
        "life_stage": family.family_life_stage,
        "ministry_focus": family.primary_ministry_focus,
        "special_pastoral_care": family.special_pastoral_care
    }

def get_member_details(member):
    """Get comprehensive member details"""
    member_doc = frappe.get_doc("Church Member", member)
    
    # Get ministry roles
    roles = []
    if member_doc.ministry_roles:
        roles = [role.role for role in member_doc.ministry_roles]
    
    # Get attendance history
    attendance = frappe.get_all("Church Attendance Detail",
        filters={"member": member},
        fields=["parent", "check_in_time", "attendance_status"],
        order_by="creation desc",
        limit=5
    )
    
    # Get small groups
    groups = frappe.get_all("Church Small Group Member",
        filters={"member": member},
        fields=["parent", "role", "join_date", "status"]
    )
    
    return {
        "name": f"{member_doc.first_name} {member_doc.last_name}",
        "email": member_doc.email,
        "phone": member_doc.phone,
        "date_of_birth": member_doc.date_of_birth,
        "join_date": member_doc.join_date,
        "status": member_doc.status,
        "address": member_doc.address,
        "city": member_doc.city,
        "state": member_doc.state,
        "country": member_doc.country,
        "family_unit": member_doc.family_unit,
        "family_role": member_doc.family_role,
        "ministry_roles": roles,
        "recent_attendance": attendance,
        "small_groups": groups
    }

def get_service_details(service):
    """Get comprehensive service details"""
    service_doc = frappe.get_doc("Church Service", service)
    
    # Get service team
    team = []
    if service_doc.service_team:
        for member in service_doc.service_team:
            team.append({
                "member": member.member,
                "role": member.role,
                "notes": member.notes
            })
    
    # Get offerings
    offerings = []
    if service_doc.offering_details:
        for offering in service_doc.offering_details:
            offerings.append({
                "type": offering.offering_type,
                "amount": offering.amount,
                "payment_method": offering.payment_method
            })
    
    return {
        "service_type": service_doc.service_type,
        "date": service_doc.date,
        "start_time": service_doc.start_time,
        "end_time": service_doc.end_time,
        "status": service_doc.status,
        "attendance_count": service_doc.attendance_count,
        "description": service_doc.description,
        "sermon_notes": service_doc.sermon_notes,
        "team": team,
        "offerings": offerings,
        "total_offering": service_doc.total_offering
    }

def send_notification(recipients, template, context):
    """Send email notification using template"""
    if isinstance(recipients, str):
        recipients = [recipients]
    
    # Get church settings
    settings = get_church_settings()
    
    # Add church info to context
    context.update(settings)
    
    # Render email content
    content = get_email_template(template, context)
    
    # Send email
    frappe.sendmail(
        recipients=recipients,
        subject=context.get("subject", f"{settings['church_name']} - Notification"),
        message=content,
        reference_doctype=context.get("reference_doctype"),
        reference_name=context.get("reference_name")
    )
