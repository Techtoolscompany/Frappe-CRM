import frappe
from frappe import _

def has_member_permission(doc, user=None, permission_type=None):
    """
    Custom permission handler for Church Member doctype
    
    Rules:
    1. System Manager can do anything
    2. Church Administrator can do anything
    3. Church Pastor can view and edit but not delete
    4. Members can view their own profiles and family members
    5. Public can view basic info if enabled in settings
    """
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
        
    if "Church Administrator" in frappe.get_roles(user):
        return True
        
    if "Church Pastor" in frappe.get_roles(user):
        if permission_type == "delete":
            return False
        return True
    
    # Check if user is viewing their own profile
    if doc.user == user:
        if permission_type in ["read", "write"]:
            return True
            
    # Check if user is viewing a family member
    user_member = frappe.get_value("Church Member", {"user": user}, "family_unit")
    if user_member and doc.family_unit and user_member == doc.family_unit:
        if permission_type == "read":
            return True
            
    settings = frappe.get_single("Church Settings")
    if settings.allow_public_member_viewing and permission_type == "read":
        return True
        
    return False

def has_family_permission(doc, user=None, permission_type=None):
    """
    Custom permission handler for Family Unit doctype
    
    Rules:
    1. System Manager can do anything
    2. Church Administrator can do anything
    3. Church Pastor can view and edit but not delete
    4. Primary contact can edit their family unit
    5. Family members can view their family unit
    """
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
        
    if "Church Administrator" in frappe.get_roles(user):
        return True
        
    if "Church Pastor" in frappe.get_roles(user):
        if permission_type == "delete":
            return False
        return True
    
    # Check if user is primary contact
    if doc.primary_contact:
        member = frappe.get_value("Church Member", 
            {"name": doc.primary_contact, "user": user})
        if member and permission_type in ["read", "write"]:
            return True
    
    # Check if user is a family member
    member = frappe.get_value("Church Member", 
        {"user": user, "family_unit": doc.name})
    if member and permission_type == "read":
        return True
    
    return False

def get_permission_query_conditions(user=None, doctype=None):
    """
    Return query conditions based on user permissions
    """
    if not user:
        user = frappe.session.user
        
    if "System Manager" in frappe.get_roles(user):
        return ""
        
    if "Church Administrator" in frappe.get_roles(user):
        return ""
        
    if "Church Pastor" in frappe.get_roles(user):
        return ""
    
    conditions = []
    
    if doctype == "Church Member":
        # User can see their own profile
        conditions.append(f"`tabChurch Member`.user = '{user}'")
        
        # User can see their family members
        family_unit = frappe.get_value("Church Member", 
            {"user": user}, "family_unit")
        if family_unit:
            conditions.append(
                f"`tabChurch Member`.family_unit = '{family_unit}'")
            
        # Public viewing if enabled
        settings = frappe.get_single("Church Settings")
        if settings.allow_public_member_viewing:
            conditions.append("`tabChurch Member`.public_profile = 1")
            
    elif doctype == "Family Unit":
        # User can see their own family unit
        member = frappe.get_value("Church Member", {"user": user}, 
            ["family_unit", "name"])
        if member:
            conditions.append(
                f"`tabFamily Unit`.name = '{member[0]}'")
            # Primary contact can see their family unit
            conditions.append(
                f"`tabFamily Unit`.primary_contact = '{member[1]}'")
    
    if conditions:
        return "(" + " OR ".join(conditions) + ")"
    
    return "1=0"  # No access by default

def apply_user_permissions(user, doc, ptype):
    """
    Apply user-specific permissions to a document
    """
    roles = frappe.get_roles(user)
    
    # System Manager and Church Administrator have full access
    if "System Manager" in roles or "Church Administrator" in roles:
        return
    
    # Church Pastor can't delete
    if "Church Pastor" in roles and ptype == "delete":
        frappe.throw(_("Church Pastors cannot delete records"))
    
    # Regular users have limited access
    if doc.doctype == "Church Member":
        if doc.user != user and ptype != "read":
            frappe.throw(_("You can only edit your own profile"))
            
    elif doc.doctype == "Family Unit":
        member = frappe.get_value("Church Member", 
            {"user": user, "family_unit": doc.name})
        if not member and ptype != "read":
            frappe.throw(
                _("You can only edit your own family unit"))
