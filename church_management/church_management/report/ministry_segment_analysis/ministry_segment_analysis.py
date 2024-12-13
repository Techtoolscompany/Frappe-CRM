import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None, get_chart_data(data)

def get_columns():
    return [
        {
            "fieldname": "segment_name",
            "label": _("Segment Name"),
            "fieldtype": "Link",
            "options": "Ministry Segment",
            "width": 180
        },
        {
            "fieldname": "total_members",
            "label": _("Total Members"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "active_members",
            "label": _("Active Members"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "email_reachable",
            "label": _("Email Reachable"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "sms_reachable",
            "label": _("SMS Reachable"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "avg_attendance",
            "label": _("Avg Attendance %"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "engagement_score",
            "label": _("Engagement Score"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 140
        },
        {
            "fieldname": "communication_rate",
            "label": _("Communication Rate"),
            "fieldtype": "Percent",
            "width": 140
        }
    ]

def get_data(filters):
    segments = frappe.get_all("Ministry Segment",
        filters={"is_active": 1},
        fields=["name", "segment_name"]
    )
    
    data = []
    for segment in segments:
        segment_doc = frappe.get_doc("Ministry Segment", segment.name)
        members = segment_doc.preview_matching_members()
        
        if not members:
            continue
            
        member_stats = get_member_stats(members)
        engagement = get_engagement_stats(members)
        communication = get_communication_stats(segment.name)
        
        data.append({
            "segment_name": segment.segment_name,
            "total_members": len(members),
            "active_members": member_stats["active"],
            "email_reachable": member_stats["email"],
            "sms_reachable": member_stats["sms"],
            "avg_attendance": engagement["attendance"],
            "engagement_score": engagement["score"],
            "communication_rate": communication["rate"]
        })
    
    return data

def get_member_stats(members):
    """Get member statistics"""
    stats = {
        "active": 0,
        "email": 0,
        "sms": 0
    }
    
    for member in members:
        if frappe.db.get_value("Church Member", member["name"], "status") == "Active":
            stats["active"] += 1
        if member.get("email"):
            stats["email"] += 1
        if member.get("phone"):
            stats["sms"] += 1
    
    return stats

def get_engagement_stats(members):
    """Get engagement statistics"""
    total_attendance = 0
    total_services = frappe.db.count("Church Service", 
        {"date": [">=", "DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"]})
    
    if not total_services:
        return {"attendance": 0, "score": 0}
    
    for member in members:
        attendance = frappe.db.count("Church Attendance Detail",
            {
                "member": member["name"],
                "parent": ["in", frappe.db.get_all("Church Service",
                    {"date": [">=", "DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"]},
                    pluck="name"
                )]
            }
        )
        total_attendance += attendance
    
    avg_attendance = (total_attendance / (len(members) * total_services)) * 100
    
    # Calculate engagement score (0-10)
    # Based on attendance and other factors
    engagement_score = min(10, (avg_attendance / 10))
    
    return {
        "attendance": avg_attendance,
        "score": engagement_score
    }

def get_communication_stats(segment_name):
    """Get communication statistics"""
    last_month = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_sent,
            COUNT(DISTINCT recipient) as unique_recipients
        FROM `tabEmail Queue`
        WHERE 
            reference_doctype = 'Ministry Segment'
            AND reference_name = %s
            AND creation >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    """, segment_name, as_dict=1)[0]
    
    rate = 0
    if last_month.unique_recipients:
        rate = (last_month.total_sent / last_month.unique_recipients) * 100
    
    return {"rate": rate}

def get_chart_data(data):
    labels = []
    engagement_scores = []
    communication_rates = []
    
    for row in data:
        labels.append(row["segment_name"])
        engagement_scores.append(row["engagement_score"])
        communication_rates.append(row["communication_rate"])
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Engagement Score",
                    "values": engagement_scores
                },
                {
                    "name": "Communication Rate",
                    "values": communication_rates
                }
            ]
        },
        "type": "bar",
        "height": 300
    }
