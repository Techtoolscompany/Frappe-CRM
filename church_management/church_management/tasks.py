import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, nowdate, get_first_day, get_last_day
from .notifications import (
    send_birthday_notifications,
    send_service_reminders,
    create_pastoral_care_alerts
)

def daily():
    """Daily scheduled tasks"""
    send_birthday_notifications()
    send_service_reminders()
    check_pastoral_care_needs()

def weekly():
    """Weekly scheduled tasks"""
    send_attendance_report()
    check_asset_maintenance()

def monthly():
    """Monthly scheduled tasks"""
    send_donation_summary()
    generate_ministry_report()

def check_pastoral_care_needs():
    """Check and create alerts for pastoral care needs"""
    create_pastoral_care_alerts()
    
    # Check for families without recent contact
    days_threshold = frappe.db.get_single_value("Church Settings", "pastoral_contact_days") or 30
    cutoff_date = add_days(nowdate(), -days_threshold)
    
    families = frappe.get_all("Family Unit",
        filters={
            "last_contact_date": ["<", cutoff_date],
            "special_pastoral_care": 0
        },
        fields=["name", "family_name"]
    )
    
    for family in families:
        frappe.get_doc({
            "doctype": "ToDo",
            "status": "Open",
            "priority": "Medium",
            "description": f"No recent contact with family: {family.family_name}",
            "reference_type": "Family Unit",
            "reference_name": family.name,
            "role": "Church Pastor"
        }).insert(ignore_permissions=True)

def check_asset_maintenance():
    """Check and create alerts for asset maintenance"""
    assets = frappe.get_all("Church Asset",
        filters={
            "next_maintenance_due": ["<=", add_days(nowdate(), 7)],
            "status": ["!=", "Under Maintenance"]
        },
        fields=["name", "asset_name", "next_maintenance_due", "custodian"]
    )
    
    for asset in assets:
        frappe.get_doc({
            "doctype": "ToDo",
            "status": "Open",
            "priority": "High" if getdate(asset.next_maintenance_due) <= getdate() else "Medium",
            "description": f"Asset Maintenance Due: {asset.asset_name}",
            "reference_type": "Church Asset",
            "reference_name": asset.name,
            "assigned_to": frappe.get_value("Church Member", asset.custodian, "user")
        }).insert(ignore_permissions=True)

def send_attendance_report():
    """Generate and send weekly attendance report"""
    last_week = add_days(nowdate(), -7)
    
    # Get attendance data
    attendance = frappe.get_all("Church Attendance",
        filters={
            "attendance_date": [">=", last_week]
        },
        fields=["attendance_date", "attendance_type", "total_attendance",
                "men_count", "women_count", "children_count"]
    )
    
    if not attendance:
        return
        
    # Calculate statistics
    total_attendance = sum(a.total_attendance for a in attendance)
    avg_attendance = total_attendance / len(attendance) if attendance else 0
    
    # Generate report
    report_html = frappe.render_template(
        "church_management/templates/emails/weekly_attendance_report.html",
        {
            "attendance": attendance,
            "total_attendance": total_attendance,
            "avg_attendance": avg_attendance,
            "date_range": f"{last_week} to {nowdate()}"
        }
    )
    
    # Send to leadership
    recipients = frappe.get_all("User",
        filters={
            "enabled": 1,
            "role": ["in", ["Church Pastor", "Church Administrator"]]
        },
        fields=["email"]
    )
    
    if recipients:
        frappe.sendmail(
            recipients=[r.email for r in recipients],
            subject=f"Weekly Attendance Report: {last_week} to {nowdate()}",
            message=report_html
        )

def send_donation_summary():
    """Generate and send monthly donation summary"""
    start_date = get_first_day(nowdate())
    end_date = get_last_day(nowdate())
    
    # Get donation data
    donations = frappe.get_all("Church Donation",
        filters={
            "donation_date": ["between", [start_date, end_date]]
        },
        fields=["donation_type", "amount"]
    )
    
    if not donations:
        return
        
    # Calculate summaries by type
    summary = {}
    for donation in donations:
        if donation.donation_type not in summary:
            summary[donation.donation_type] = 0
        summary[donation.donation_type] += donation.amount
    
    # Generate report
    report_html = frappe.render_template(
        "church_management/templates/emails/monthly_donation_summary.html",
        {
            "summary": summary,
            "total": sum(summary.values()),
            "month": start_date.strftime("%B %Y")
        }
    )
    
    # Send to administrators
    recipients = frappe.get_all("User",
        filters={
            "enabled": 1,
            "role": "Church Administrator"
        },
        fields=["email"]
    )
    
    if recipients:
        frappe.sendmail(
            recipients=[r.email for r in recipients],
            subject=f"Monthly Donation Summary: {start_date.strftime('%B %Y')}",
            message=report_html
        )

def generate_ministry_report():
    """Generate monthly ministry activity report"""
    start_date = get_first_day(nowdate())
    end_date = get_last_day(nowdate())
    
    # Gather ministry statistics
    stats = {
        "services": frappe.db.count("Church Service",
            {"date": ["between", [start_date, end_date]]}),
        "events": frappe.db.count("Church Event",
            {"start_date": ["between", [start_date, end_date]]}),
        "new_members": frappe.db.count("Church Member",
            {"join_date": ["between", [start_date, end_date]]}),
        "active_groups": frappe.db.count("Church Small Group",
            {"status": "Active"}),
        "pastoral_visits": frappe.db.count("ToDo",
            {
                "reference_type": "Family Unit",
                "status": "Completed",
                "modified": ["between", [start_date, end_date]]
            })
    }
    
    # Generate report
    report_html = frappe.render_template(
        "church_management/templates/emails/monthly_ministry_report.html",
        {
            "stats": stats,
            "month": start_date.strftime("%B %Y")
        }
    )
    
    # Send to leadership
    recipients = frappe.get_all("User",
        filters={
            "enabled": 1,
            "role": ["in", ["Church Pastor", "Church Administrator"]]
        },
        fields=["email"]
    )
    
    if recipients:
        frappe.sendmail(
            recipients=[r.email for r in recipients],
            subject=f"Monthly Ministry Report: {start_date.strftime('%B %Y')}",
            message=report_html
        )
