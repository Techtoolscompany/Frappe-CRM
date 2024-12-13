import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class FamilyUnit(Document):
    def validate(self):
        self.validate_primary_contact()
        self.update_member_counts()
        self.validate_family_tags()
    
    def validate_primary_contact(self):
        """Validate primary contact settings"""
        if self.primary_contact:
            # Verify primary contact is a member of this family
            member = frappe.get_doc("Church Member", self.primary_contact)
            if member.primary_family_unit != self.name:
                frappe.throw(
                    _("Primary contact must be a member of this family unit")
                )
            
            # Ensure primary contact flag is set on member
            if not member.family_primary_contact:
                member.family_primary_contact = 1
                member.save()
                
            # Update contact information
            self.contact_phone = member.phone
            self.contact_email = member.email
    
    def update_member_counts(self):
        """Update member count statistics"""
        members = self.get_family_members()
        
        # Count by role
        role_counts = {
            "Head of Household": 0,
            "Spouse": 0,
            "Child": 0,
            "Dependent": 0,
            "Other": 0
        }
        
        for member in members:
            role = member.get("family_role", "Other")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Set counts as custom fields
        for role, count in role_counts.items():
            field_name = f"{role.lower().replace(' ', '_')}_count"
            if hasattr(self, field_name):
                setattr(self, field_name, count)
        
        # Set total count
        self.total_members = len(members)
    
    def validate_family_tags(self):
        """Validate family tags"""
        if self.family_tags:
            # Check for duplicate tags
            seen_tags = set()
            for tag in self.family_tags:
                tag_key = (tag.tag_category, tag.tag_value)
                if tag_key in seen_tags:
                    frappe.throw(
                        _("Duplicate tag: {0} - {1}").format(
                            tag.tag_category, tag.tag_value
                        )
                    )
                seen_tags.add(tag_key)
    
    def get_family_members(self, include_inactive=False):
        """Get all family members"""
        filters = {"primary_family_unit": self.name}
        if not include_inactive:
            filters["status"] = "Active"
            
        members = frappe.get_all("Church Member",
            filters=filters,
            fields=[
                "name", "first_name", "last_name",
                "family_role", "family_status",
                "family_primary_contact", "email", "phone"
            ]
        )
        return members
    
    def get_secondary_members(self, include_inactive=False):
        """Get members from secondary family relationships"""
        members = []
        
        # Get members who have this as secondary family unit
        secondary = frappe.get_all("Secondary Family Unit",
            filters={
                "family_unit": self.name,
                "is_active": 1
            },
            fields=["parent", "relationship_type"]
        )
        
        for sec in secondary:
            member = frappe.get_doc("Church Member", sec.parent)
            if include_inactive or member.status == "Active":
                members.append({
                    "name": member.name,
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "relationship": sec.relationship_type,
                    "email": member.email,
                    "phone": member.phone
                })
        
        return members
    
    def get_family_relationships(self):
        """Get all family relationships"""
        relationships = []
        members = self.get_family_members(include_inactive=True)
        
        for member in members:
            # Get relationships for this member
            member_rels = frappe.get_all("Family Relationship",
                filters={
                    "member": member.name,
                    "is_active": 1
                },
                fields=[
                    "related_member", "relationship_type",
                    "start_date", "notes"
                ]
            )
            
            for rel in member_rels:
                related = frappe.get_doc("Church Member", rel.related_member)
                relationships.append({
                    "member": member.name,
                    "member_name": f"{member.first_name} {member.last_name}",
                    "related": rel.related_member,
                    "related_name": f"{related.first_name} {related.last_name}",
                    "relationship": rel.relationship_type,
                    "start_date": rel.start_date,
                    "notes": rel.notes
                })
        
        return relationships
    
    def get_communication_preferences(self):
        """Get family communication preferences"""
        preferences = {
            "allow_home_visits": True,
            "allow_phone_calls": True,
            "allow_emails": True,
            "preferred_contact_time": None,
            "preferred_contact_day": None,
            "preferred_language": None
        }
        
        # Get preferences from primary contact
        if self.primary_contact:
            member = frappe.get_doc("Church Member", self.primary_contact)
            preferences.update({
                "allow_home_visits": member.allow_home_visits,
                "allow_phone_calls": member.allow_phone_calls,
                "allow_emails": member.allow_emails,
                "preferred_contact_time": member.preferred_contact_time,
                "preferred_contact_day": member.preferred_contact_day,
                "preferred_language": member.preferred_language
            })
        
        return preferences
