import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class ChurchMember(Document):
    def validate(self):
        self.validate_family_relationships()
        self.validate_primary_contact()
        self.track_family_changes()
    
    def validate_family_relationships(self):
        """Validate family relationships"""
        if self.family_relationships:
            # Check for duplicate relationships
            relationships = []
            for rel in self.family_relationships:
                key = (rel.related_member, rel.relationship_type)
                if key in relationships:
                    frappe.throw(
                        _("Duplicate relationship with member {0}").format(
                            rel.related_member
                        )
                    )
                relationships.append(key)
                
                # Validate relationship dates
                if rel.end_date and getdate(rel.start_date) > getdate(rel.end_date):
                    frappe.throw(
                        _("End date cannot be before start date for {0}").format(
                            rel.related_member
                        )
                    )
    
    def validate_primary_contact(self):
        """Validate primary contact settings"""
        if self.family_primary_contact and not self.primary_family_unit:
            frappe.throw(
                _("Primary Family Unit is required for primary contact")
            )
            
        if self.family_primary_contact:
            # Check if another member is already primary contact
            existing = frappe.get_all("Church Member",
                filters={
                    "primary_family_unit": self.primary_family_unit,
                    "family_primary_contact": 1,
                    "name": ["!=", self.name]
                }
            )
            if existing:
                # Unset their primary contact status
                for member in existing:
                    frappe.db.set_value("Church Member", 
                        member.name, "family_primary_contact", 0)
                
                # Update Family Unit's primary contact
                frappe.db.set_value("Family Unit", 
                    self.primary_family_unit, "primary_contact", self.name)
    
    def track_family_changes(self):
        """Track changes in family information"""
        if not self.is_new():
            old_doc = self.get_doc_before_save()
            
            # Check for family role changes
            if old_doc.family_role != self.family_role:
                self.create_family_history("Role Change", {
                    "old_family_role": old_doc.family_role,
                    "new_family_role": self.family_role
                })
            
            # Check for family status changes
            if old_doc.family_status != self.family_status:
                self.create_family_history("Status Change", {
                    "old_family_status": old_doc.family_status,
                    "new_family_status": self.family_status
                })
            
            # Check for primary contact changes
            if old_doc.family_primary_contact != self.family_primary_contact:
                self.create_family_history("Primary Contact Change", {
                    "old_primary_contact": old_doc.family_primary_contact,
                    "new_primary_contact": self.family_primary_contact
                })
            
            # Check for family unit changes
            if old_doc.primary_family_unit != self.primary_family_unit:
                self.create_family_history("Family Unit Change", {
                    "old_family_unit": old_doc.primary_family_unit,
                    "new_family_unit": self.primary_family_unit
                })
    
    def create_family_history(self, change_type, values):
        """Create family history record"""
        history = frappe.get_doc({
            "doctype": "Family History",
            "member": self.name,
            "family_unit": self.primary_family_unit,
            "change_type": change_type,
            "change_date": getdate(),
            "changed_by": frappe.session.user,
            "old_family_role": values.get("old_family_role"),
            "new_family_role": values.get("new_family_role"),
            "old_family_status": values.get("old_family_status"),
            "new_family_status": values.get("new_family_status"),
            "old_primary_contact": values.get("old_primary_contact", 0),
            "new_primary_contact": values.get("new_primary_contact", 0),
            "change_reason": "System Update"
        })
        history.insert(ignore_permissions=True)
    
    def get_family_members(self):
        """Get all family members"""
        members = []
        
        # Get members from primary family unit
        if self.primary_family_unit:
            members.extend(frappe.get_all("Church Member",
                filters={"primary_family_unit": self.primary_family_unit},
                fields=["name", "first_name", "last_name", "family_role"]
            ))
        
        # Get members from secondary family units
        if self.secondary_family_units:
            for unit in self.secondary_family_units:
                if unit.is_active:
                    members.extend(frappe.get_all("Church Member",
                        filters={"primary_family_unit": unit.family_unit},
                        fields=["name", "first_name", "last_name", "family_role"]
                    ))
        
        return members
    
    def get_active_relationships(self):
        """Get active family relationships"""
        relationships = []
        if self.family_relationships:
            for rel in self.family_relationships:
                if rel.is_active:
                    member = frappe.get_doc("Church Member", rel.related_member)
                    relationships.append({
                        "member": rel.related_member,
                        "name": f"{member.first_name} {member.last_name}",
                        "relationship": rel.relationship_type,
                        "start_date": rel.start_date
                    })
        return relationships
