import frappe
from frappe import _
from frappe.utils import getdate, add_months, add_days

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None, get_chart_data(data)

def get_columns():
    return [
        {
            "fieldname": "member",
            "label": _("Member"),
            "fieldtype": "Link",
            "options": "Church Member",
            "width": 180
        },
        {
            "fieldname": "member_name",
            "label": _("Member Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "total_engagements",
            "label": _("Total Engagements"),
            "fieldtype": "Int",
            "width": 130
        },
        {
            "fieldname": "avg_score",
            "label": _("Average Score"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 120
        },
        {
            "fieldname": "attendance_rate",
            "label": _("Attendance Rate %"),
            "fieldtype": "Percent",
            "width": 130
        },
        {
            "fieldname": "ministry_involvement",
            "label": _("Ministry Involvement"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "event_participation",
            "label": _("Event Participation"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "small_group_attendance",
            "label": _("Small Group Attendance"),
            "fieldtype": "Int",
            "width": 170
        },
        {
            "fieldname": "trend",
            "label": _("Trend"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "last_engagement",
            "label": _("Last Engagement"),
            "fieldtype": "Date",
            "width": 120
        }
    ]

def get_data(filters):
    members = get_members(filters)
    data = []
    
    for member in members:
        engagement_stats = get_member_engagement_stats(member.name, filters)
        if engagement_stats["total_engagements"] > 0:
            data.append({
                "member": member.name,
                "member_name": f"{member.first_name} {member.last_name}",
                "total_engagements": engagement_stats["total_engagements"],
                "avg_score": engagement_stats["avg_score"],
                "attendance_rate": engagement_stats["attendance_rate"],
                "ministry_involvement": engagement_stats["ministry_involvement"],
                "event_participation": engagement_stats["event_participation"],
                "small_group_attendance": engagement_stats["small_group_attendance"],
                "trend": engagement_stats["trend"],
                "last_engagement": engagement_stats["last_engagement"]
            })
    
    return data

def get_members(filters):
    conditions = {"status": "Active"}
    
    if filters.get("member_group"):
        conditions["member_group"] = filters.get("member_group")
    
    return frappe.get_all("Church Member",
        filters=conditions,
        fields=["name", "first_name", "last_name"]
    )

def get_member_engagement_stats(member, filters):
    date_filters = {
        "member": member,
        "status": "Active"
    }
    
    if filters.get("from_date"):
        date_filters["date"] = [">=", filters.get("from_date")]
    if filters.get("to_date"):
        date_filters["date"] = ["<=", filters.get("to_date")]
    
    engagements = frappe.get_all("Member Engagement",
        filters=date_filters,
        fields=[
            "engagement_type", "engagement_score", "date",
            "trend", "duration"
        ]
    )
    
    if not engagements:
        return get_empty_stats()
    
    stats = {
        "total_engagements": len(engagements),
        "avg_score": sum(e.engagement_score for e in engagements) / len(engagements),
        "attendance_rate": calculate_attendance_rate(member, filters),
        "ministry_involvement": len([e for e in engagements if e.engagement_type == "Ministry"]),
        "event_participation": len([e for e in engagements if e.engagement_type == "Event"]),
        "small_group_attendance": len([e for e in engagements if e.engagement_type == "Small Group"]),
        "trend": get_overall_trend(engagements),
        "last_engagement": max(getdate(e.date) for e in engagements)
    }
    
    return stats

def get_empty_stats():
    return {
        "total_engagements": 0,
        "avg_score": 0,
        "attendance_rate": 0,
        "ministry_involvement": 0,
        "event_participation": 0,
        "small_group_attendance": 0,
        "trend": "N/A",
        "last_engagement": None
    }

def calculate_attendance_rate(member, filters):
    """Calculate attendance rate for the period"""
    date_filters = {
        "date": ["between", [
            filters.get("from_date", add_months(getdate(), -3)),
            filters.get("to_date", getdate())
