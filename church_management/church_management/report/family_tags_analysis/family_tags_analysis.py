import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None, get_chart_data(data)

def get_columns():
    return [
        {
            "fieldname": "tag_category",
            "label": _("Tag Category"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "tag_value",
            "label": _("Tag Value"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "family_count",
            "label": _("Number of Families"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "member_count",
            "label": _("Total Members"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "avg_attendance",
            "label": _("Average Attendance"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 150
        },
        {
            "fieldname": "pastoral_care_count",
            "label": _("Pastoral Care Needed"),
            "fieldtype": "Int",
            "width": 150
        }
    ]

def get_data(filters):
    data = []
    
    # Get all family tags
    tags = frappe.db.sql("""
        SELECT 
            ft.tag_category,
            ft.tag_value,
            COUNT(DISTINCT ft.parent) as family_count
        FROM 
            `tabFamily Tag` ft
        GROUP BY 
            ft.tag_category, ft.tag_value
    """, as_dict=1)
    
    for tag in tags:
        # Get families with this tag
        families = frappe.db.sql("""
            SELECT 
                fu.name,
                fu.special_pastoral_care
            FROM 
                `tabFamily Unit` fu
                INNER JOIN `tabFamily Tag` ft ON ft.parent = fu.name
            WHERE 
                ft.tag_category = %s AND ft.tag_value = %s
        """, (tag.tag_category, tag.tag_value), as_dict=1)
        
        family_names = [f.name for f in families]
        
        # Get member count for these families
        member_count = frappe.db.count("Church Member", {"family_unit": ["in", family_names]})
        
        # Get average attendance
        attendance = frappe.db.sql("""
            SELECT 
                AVG(ca.total_attendance) as avg_attendance
            FROM 
                `tabChurch Attendance` ca
                INNER JOIN `tabChurch Member` cm ON cm.name = ca.recorded_by
            WHERE 
                cm.family_unit IN %s
        """, [family_names], as_dict=1)
        
        # Count families needing pastoral care
        pastoral_care_count = len([f for f in families if f.special_pastoral_care])
        
        data.append({
            "tag_category": tag.tag_category,
            "tag_value": tag.tag_value,
            "family_count": tag.family_count,
            "member_count": member_count,
            "avg_attendance": attendance[0].avg_attendance if attendance[0].avg_attendance else 0,
            "pastoral_care_count": pastoral_care_count
        })
    
    return data

def get_chart_data(data):
    categories = list(set([d["tag_category"] for d in data]))
    datasets = []
    
    for category in categories:
        category_data = [d for d in data if d["tag_category"] == category]
        datasets.append({
            "name": category,
            "values": [d["family_count"] for d in category_data]
        })
    
    chart = {
        "data": {
            "labels": list(set([d["tag_value"] for d in data])),
            "datasets": datasets
        },
        "type": "bar",
        "height": 300
    }
    
    return chart
