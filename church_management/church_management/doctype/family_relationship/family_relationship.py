import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class FamilyRelationship(Document):
    def validate(self):
        self.validate_members()
        self.validate_dates()
        self.create_reciprocal_relationship()
    
    def validate_members(self):
        """Validate member relationships"""
        if self.member == self.related_member:
            frappe.throw(_("Cannot create relationship with self"))
            
        # Check if relationship already exists
        existing = frappe.get_all("Family Relationship",
            filters={
                "member": self.member,
                "related_member": self.related_member,
                "name": ["!=", self.name]
            }
        )
        if existing:
            frappe.throw(
                _("Relationship already exists between {0} and {1}").format(
                    self.member, self.related_member
                )
            )
    
    def validate_dates(self):
        """Validate relationship dates"""
        if self.end_date and getdate(self.start_date) > getdate(self.end_date):
            frappe.throw(_("End date cannot be before start date"))
    
    def create_reciprocal_relationship(self):
        """Create or update reciprocal relationship"""
        if not self.is_new():
            return
            
        # Define reciprocal relationship types
        reciprocal_types = {
            "Spouse": "Spouse",
            "Parent": "Child",
            "Child": "Parent",
            "Sibling": "Sibling",
            "Grandparent": "Grandchild",
            "Grandchild": "Grandparent",
            "Guardian": "Ward",
            "Ward": "Guardian"
        }
        
        if self.relationship_type in reciprocal_types:
            # Check if reciprocal relationship exists
            existing = frappe.get_all("Family Relationship",
                filters={
                    "member": self.related_member,
                    "related_member": self.member
                }
            )
            
            if not existing:
                # Create reciprocal relationship
                reciprocal = frappe.get_doc({
                    "doctype": "Family Relationship",
                    "member": self.related_member,
                    "related_member": self.member,
                    "relationship_type": reciprocal_types[self.relationship_type],
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "is_active": self.is_active,
                    "notes": self.notes
                })
                reciprocal.flags.ignore_validate = True
                reciprocal.insert(ignore_permissions=True)
    
    def on_update(self):
        """Update reciprocal relationship"""
        if not self.flags.ignore_validate:
            # Update reciprocal relationship
            reciprocal = frappe.get_all("Family Relationship",
                filters={
                    "member": self.related_member,
                    "related_member": self.member
                }
            )
            
            if reciprocal:
                frappe.db.set_value("Family Relationship", reciprocal[0].name, {
                    "end_date": self.end_date,
                    "is_active": self.is_active,
                    "notes": self.notes
                })
    
    def on_trash(self):
        """Delete reciprocal relationship"""
        reciprocal = frappe.get_all("Family Relationship",
            filters={
                "member": self.related_member,
                "related_member": self.member
            }
        )
        
        if reciprocal:
            frappe.delete_doc("Family Relationship", 
                reciprocal[0].name, ignore_permissions=True)
    
    def get_relationship_details(self):
        """Get formatted relationship details"""
        member = frappe.get_doc("Church Member", self.member)
        related = frappe.get_doc("Church Member", self.related_member)
        
        return {
            "member_name": f"{member.first_name} {member.last_name}",
            "related_name": f"{related.first_name} {related.last_name}",
            "relationship": self.relationship_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_active": self.is_active,
            "notes": self.notes
        }
