import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None, get_chart_data(data)

def get_columns():
    return [
        {
            "fieldname": "family_unit",
            "label": _("Family Unit"),
            "fieldtype": "Link",
            "options": "Family Unit",
            "width": 180
        },
        {
            "fieldname": "family_name",
            "label": _("Family Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "total_members",
            "label": _("Total Members"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "head_of_household",
            "label": _("Head of Household"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "spouse_count",
            "label": _("Spouses"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "child_count",
            "label": _("Children"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "dependent_count",
            "label": _("Dependents"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "secondary_members",
            "label": _("Secondary Members"),
            "fieldtype": "Int",
            "width": 140
        },
        {
            "fieldname": "active_relationships",
            "label": _("Active Relationships"),
            "fieldtype": "Int",
            "width": 140
        },
        {
            "fieldname": "family_status",
            "label": _("Family Status"),
            "fieldtype": "Data",
            "width": 120
        }
    ]

def get_data(filters):
    data = []
    
    # Get all family units
    family_units = frappe.get_all("Family Unit",
        fields=["name", "family_name", "primary_contact"],
        filters=filters
    )
    
    for family in family_units:
        family_doc = frappe.get_doc("Family Unit", family.name)
        members = family_doc.get_family_members()
        secondary = family_doc.get_secondary_members()
        relationships = family_doc.get_family_relationships()
        
        # Count members by role
        role_counts = {
            "Head of Household": 0,
            "Spouse": 0,
            "Child": 0,
            "Dependent": 0,
            "Other": 0
        }
        
        head_name = ""
        for member in members:
            role = member.get("family_role", "Other")
            role_counts[role] = role_counts.get(role, 0) + 1
            if role == "Head of Household":
                head_name = f"{member.get('first_name')} {member.get('last_name')}"
        
        # Determine family status
        if not members:
            family_status = "Inactive"
        elif len(members) == 1:
            family_status = "Single Member"
        elif role_counts["Head of Household"] == 0:
            family_status = "No Head"
        elif role_counts["Spouse"] == 0:
            family_status = "Single Parent" if role_counts["Child"] > 0 else "Single"
        else:
            family_status = "Complete"
        
        data.append({
            "family_unit": family.name,
            "family_name": family.family_name,
            "total_members": len(members),
            "head_of_household": head_name,
            "spouse_count": role_counts["Spouse"],
            "child_count": role_counts["Child"],
            "dependent_count": role_counts["Dependent"],
            "secondary_members": len(secondary),
            "active_relationships": len(relationships),
            "family_status": family_status
        })
    
    return data

def get_chart_data(data):
    labels = []
    family_sizes = []
    relationship_counts = []
    
    for row in data:
        labels.append(row["family_name"])
        family_sizes.append(row["total_members"])
        relationship_counts.append(row["active_relationships"])
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Family Size",
                    "values": family_sizes
                },
                {
                    "name": "Relationships",
                    "values": relationship_counts
                }
            ]
        },
        "type": "bar",
        "height": 300
    }

def get_report_summary(data):
    total_families = len(data)
    total_members = sum(d["total_members"] for d in data)
    total_children = sum(d["child_count"] for d in data)
    total_relationships = sum(d["active_relationships"] for d in data)
    
    status_counts = {}
    for row in data:
        status = row["family_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return [
        {
            "value": total_families,
            "label": _("Total Families"),
            "datatype": "Int",
            "width": "150px"
        },
        {
            "value": total_members,
            "label": _("Total Members"),
            "datatype": "Int",
            "width": "150px"
        },
        {
            "value": total_children,
            "label": _("Total Children"),
            "datatype": "Int",
            "width": "150px"
        },
        {
            "value": total_relationships,
            "label": _("Active Relationships"),
            "datatype": "Int",
            "width": "150px"
        },
        {
            "value": status_counts.get("Complete", 0),
            "label": _("Complete Families"),
            "datatype": "Int",
            "width": "150px"
        }
    ]
