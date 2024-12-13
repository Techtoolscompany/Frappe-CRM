import frappe
from frappe.utils import (
    flt, cint, cstr, getdate, get_datetime,
    format_datetime, format_date, format_time,
    strip_html
)
from datetime import datetime
from .utils import get_church_settings

def get_filters():
    """Return filters available in templates"""
    return {
        "format_phone": format_phone,
        "format_address": format_address,
        "format_duration": format_duration,
        "format_attendance": format_attendance,
        "format_age": format_age,
        "format_family_role": format_family_role,
        "format_ministry_role": format_ministry_role,
        "format_donation_type": format_donation_type,
        "format_payment_method": format_payment_method,
        "format_service_type": format_service_type,
        "format_event_type": format_event_type,
        "format_asset_status": format_asset_status,
        "strip_html_tags": strip_html_tags,
        "truncate": truncate,
        "time_ago": time_ago
    }

def format_phone(phone):
    """Format phone number"""
    if not phone:
        return ""
    # Remove non-numeric characters
    phone = "".join(filter(str.isdigit, str(phone)))
    # Format based on length
    if len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone

def format_address(address, city=None, state=None, country=None):
    """Format complete address"""
    parts = []
    if address:
        parts.append(address)
    if city:
        parts.append(city)
    if state:
        parts.append(state)
    if country:
        parts.append(country)
    return ", ".join(filter(None, parts))

def format_duration(minutes):
    """Format duration in minutes to readable format"""
    if not minutes:
        return ""
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return f"{hours}h {mins}m"
    elif hours:
        return f"{hours}h"
    return f"{mins}m"

def format_attendance(count, total=None):
    """Format attendance count with optional percentage"""
    if not count:
        return "0"
    if total:
        percentage = (count / total) * 100
        return f"{count} ({percentage:.1f}%)"
    return str(count)

def format_age(date_of_birth):
    """Format age from date of birth"""
    if not date_of_birth:
        return ""
    today = getdate()
    dob = getdate(date_of_birth)
    age = (today - dob).days // 365
    return str(age)

def format_family_role(role):
    """Format family role with color coding"""
    colors = {
        "Head of Household": "text-blue-600",
        "Spouse": "text-purple-600",
        "Child": "text-green-600",
        "Dependent": "text-yellow-600",
        "Other": "text-gray-600"
    }
    color_class = colors.get(role, "text-gray-600")
    return f'<span class="{color_class}">{role}</span>'

def format_ministry_role(role):
    """Format ministry role name"""
    if not role:
        return ""
    role_doc = frappe.get_doc("Church Ministry Role", role)
    return f"{role_doc.role_name} ({role_doc.department})"

def format_donation_type(dtype):
    """Format donation type with color coding"""
    colors = {
        "Tithe": "text-green-600",
        "General Offering": "text-blue-600",
        "Mission Offering": "text-purple-600",
        "Building Fund": "text-yellow-600",
        "Special Offering": "text-red-600"
    }
    color_class = colors.get(dtype, "text-gray-600")
    return f'<span class="{color_class}">{dtype}</span>'

def format_payment_method(method):
    """Format payment method with icon"""
    icons = {
        "Cash": "💵",
        "Check": "📝",
        "Bank Transfer": "🏦",
        "Credit Card": "💳",
        "Mobile Money": "📱"
    }
    icon = icons.get(method, "💰")
    return f"{icon} {method}"

def format_service_type(stype):
    """Format service type with color coding"""
    colors = {
        "Sunday Service": "text-blue-600",
        "Midweek Service": "text-green-600",
        "Prayer Meeting": "text-purple-600",
        "Special Event": "text-red-600",
        "Youth Service": "text-yellow-600"
    }
    color_class = colors.get(stype, "text-gray-600")
    return f'<span class="{color_class}">{stype}</span>'

def format_event_type(etype):
    """Format event type with icon"""
    icons = {
        "Conference": "🎤",
        "Retreat": "🏕️",
        "Youth Camp": "⛺",
        "Workshop": "📚",
        "Seminar": "🎯",
        "Outreach": "🤝",
        "Fellowship": "👥"
    }
    icon = icons.get(etype, "📅")
    return f"{icon} {etype}"

def format_asset_status(status):
    """Format asset status with color coding"""
    colors = {
        "In Use": "text-green-600",
        "In Storage": "text-blue-600",
        "Under Maintenance": "text-yellow-600",
        "Disposed": "text-red-600",
        "Lost/Damaged": "text-gray-600"
    }
    color_class = colors.get(status, "text-gray-600")
    return f'<span class="{color_class}">{status}</span>'

def strip_html_tags(text):
    """Remove HTML tags from text"""
    return strip_html(cstr(text))

def truncate(text, length=100, suffix="..."):
    """Truncate text to specified length"""
    text = cstr(text)
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + suffix

def time_ago(date):
    """Convert date to relative time format"""
    if not date:
        return ""
    
    if isinstance(date, str):
        date = get_datetime(date)
    
    now = datetime.now()
    diff = now - date
    
    days = diff.days
    seconds = diff.seconds
    
    if days > 365:
        years = days // 365
        return f"{years}y ago"
    elif days > 30:
        months = days // 30
        return f"{months}m ago"
    elif days > 0:
        return f"{days}d ago"
    elif seconds > 3600:
        hours = seconds // 3600
        return f"{hours}h ago"
    elif seconds > 60:
        minutes = seconds // 60
        return f"{minutes}m ago"
    return "just now"
