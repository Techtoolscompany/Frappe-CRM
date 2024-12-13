import frappe
from frappe.utils import (
    flt, fmt_money, format_datetime, format_date,
    get_url, get_datetime, getdate, nowdate,
    add_days, add_months
)
from .utils import get_church_settings

def get_methods():
    """Return methods available in templates"""
    return {
        "format_currency": format_currency,
        "format_percent": format_percent,
        "get_member_name": get_member_name,
        "get_family_name": get_family_name,
        "get_role_name": get_role_name,
        "get_attendance_stats": get_attendance_stats,
        "get_donation_stats": get_donation_stats,
        "get_ministry_stats": get_ministry_stats,
        "get_age_group": get_age_group,
        "get_member_status_label": get_member_status_label,
        "get_service_status_label": get_service_status_label,
        "get_pastoral_care_label": get_pastoral_care_label,
        "get_life_stage_label": get_life_stage_label,
        "get_church_logo_url": get_church_logo_url,
        "get_app_url": get_app_url
    }

def format_currency(amount, currency=None):
    """Format currency with church's default currency"""
    if not currency:
        settings = get_church_settings()
        currency = settings.get("default_currency")
    return fmt_money(amount, currency=currency)

def format_percent(value, decimals=1):
    """Format number as percentage"""
    return f"{flt(value, decimals)}%"

def get_member_name(member):
    """Get full name of church member"""
    if not member:
        return ""
    doc = frappe.get_doc("Church Member", member)
    return f"{doc.first_name} {doc.last_name}"

def get_family_name(family_unit):
    """Get family unit name"""
    if not family_unit:
        return ""
    return frappe.get_value("Family Unit", family_unit, "family_name")

def get_role_name(role):
    """Get ministry role name"""
    if not role:
        return ""
    return frappe.get_value("Church Ministry Role", role, "role_name")

def get_attendance_stats(date_from=None, date_to=None):
    """Get attendance statistics for date range"""
    if not date_from:
        date_from = add_months(nowdate(), -1)
    if not date_to:
        date_to = nowdate()
        
    attendance = frappe.get_all("Church Attendance",
        filters={
            "attendance_date": ["between", [date_from, date_to]]
        },
        fields=["total_attendance", "men_count", "women_count", "children_count"]
    )
    
    stats = {
        "total": sum(a.total_attendance for a in attendance),
        "average": sum(a.total_attendance for a in attendance) / len(attendance) if attendance else 0,
        "men": sum(a.men_count for a in attendance),
        "women": sum(a.women_count for a in attendance),
        "children": sum(a.children_count for a in attendance)
    }
    
    return stats

def get_donation_stats(date_from=None, date_to=None):
    """Get donation statistics for date range"""
    if not date_from:
        date_from = add_months(nowdate(), -1)
    if not date_to:
        date_to = nowdate()
        
    donations = frappe.get_all("Church Donation",
        filters={
            "donation_date": ["between", [date_from, date_to]]
        },
        fields=["donation_type", "amount"]
    )
    
    stats = {}
    for donation in donations:
        if donation.donation_type not in stats:
            stats[donation.donation_type] = 0
        stats[donation.donation_type] += donation.amount
    
    return stats

def get_ministry_stats(date_from=None, date_to=None):
    """Get ministry statistics for date range"""
    if not date_from:
        date_from = add_months(nowdate(), -1)
    if not date_to:
        date_to = nowdate()
        
    stats = {
        "services": frappe.db.count("Church Service",
            {"date": ["between", [date_from, date_to]]}),
        "events": frappe.db.count("Church Event",
            {"start_date": ["between", [date_from, date_to]]}),
        "new_members": frappe.db.count("Church Member",
            {"join_date": ["between", [date_from, date_to]]}),
        "active_groups": frappe.db.count("Church Small Group",
            {"status": "Active"})
    }
    
    return stats

def get_age_group(date_of_birth):
    """Get age group label based on date of birth"""
    if not date_of_birth:
        return ""
        
    age = (getdate() - getdate(date_of_birth)).days // 365
    
    if age < 13:
        return "Children"
    elif age < 20:
        return "Youth"
    elif age < 30:
        return "Young Adult"
    elif age < 60:
        return "Adult"
    else:
        return "Senior"

def get_member_status_label(status):
    """Get formatted member status label"""
    labels = {
        "Active": '<span class="text-green-600">Active</span>',
        "Inactive": '<span class="text-red-600">Inactive</span>',
        "Visitor": '<span class="text-blue-600">Visitor</span>'
    }
    return labels.get(status, status)

def get_service_status_label(status):
    """Get formatted service status label"""
    labels = {
        "Scheduled": '<span class="text-blue-600">Scheduled</span>',
        "In Progress": '<span class="text-yellow-600">In Progress</span>',
        "Completed": '<span class="text-green-600">Completed</span>',
        "Cancelled": '<span class="text-red-600">Cancelled</span>'
    }
    return labels.get(status, status)

def get_pastoral_care_label(needs_care):
    """Get formatted pastoral care label"""
    if needs_care:
        return '<span class="text-red-600 font-bold">Needs Care</span>'
    return '<span class="text-green-600">Regular Care</span>'

def get_life_stage_label(stage):
    """Get formatted life stage label"""
    labels = {
        "New Family": '<span class="text-purple-600">New Family</span>',
        "Young Family": '<span class="text-blue-600">Young Family</span>',
        "Teen Family": '<span class="text-green-600">Teen Family</span>',
        "Empty Nest": '<span class="text-yellow-600">Empty Nest</span>',
        "Single Parent": '<span class="text-red-600">Single Parent</span>'
    }
    return labels.get(stage, stage)

def get_church_logo_url():
    """Get church logo URL"""
    return get_url("/assets/crm/images/logo.svg")

def get_app_url(path=""):
    """Get application URL with optional path"""
    return get_url(f"/church{path}")
