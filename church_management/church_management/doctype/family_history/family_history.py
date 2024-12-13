import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class FamilyHistory(Document):
    def validate(self):
        self.validate_dates()
        self.validate_changes()
        self.set_change_details()
    
    def validate_dates(self):
        """Validate history dates"""
        if getdate(self.change_date) > getdate():
            frappe.throw(_("Change date cannot be in the future"))
    
    def validate_changes(self):
        """Validate change type and values"""
        if self.change_type == "Role Change":
            if not (self.old_family_role or self.new_family_role):
                frappe.throw(_("Role change requires old or new role"))
                
        elif self.change_type == "Status Change":
            if not (self.old_family_status or self.new_family_status):
                frappe.throw(_("Status change requires old or new status"))
                
        elif self.change_type == "Primary Contact Change":
            if self.old_primary_contact == self.new_primary_contact:
                frappe.throw(_("Primary contact status must change"))
                
        elif self.change_type == "Family Unit Change":
            if not self.family_unit:
                frappe.throw(_("Family unit is required for unit change"))
    
    def set_change_details(self):
        """Set additional change details"""
        member = frappe.get_doc("Church Member", self.member)
        
        # Set member details
        self.member_name = f"{member.first_name} {member.last_name}"
        
        # Set family unit details if available
        if self.family_unit:
            self.family_name = frappe.db.get_value(
                "Family Unit", self.family_unit, "family_name"
            )
        
        # Set change summary based on type
        summaries = {
            "Role Change": f"Role changed from {self.old_family_role or 'None'} to {self.new_family_role or 'None'}",
            "Status Change": f"Status changed from {self.old_family_status or 'None'} to {self.new_family_status or 'None'}",
            "Primary Contact Change": "Changed primary contact status",
            "Family Unit Change": "Changed family unit assignment",
            "Relationship Change": "Updated family relationships"
        }
        self.change_summary = summaries.get(self.change_type, "")
    
    def after_insert(self):
        """After insert actions"""
        self.notify_changes()
    
    def notify_changes(self):
        """Notify relevant users about changes"""
        # Get church pastors and administrators
        recipients = []
        roles = ["Church Pastor", "Church Administrator"]
        
        for role in roles:
            users = frappe.get_all("Has Role",
                filters={
                    "role": role,
                    "parenttype": "User"
                },
                fields=["parent"]
            )
            recipients.extend([u.parent for u in users])
        
        if recipients:
            subject = f"Family Change: {self.member_name}"
            message = f"""
                <p>A family change has been recorded:</p>
                <ul>
                    <li>Member: {self.member_name}</li>
                    <li>Family: {self.family_name or 'N/A'}</li>
                    <li>Change Type: {self.change_type}</li>
                    <li>Change Date: {self.change_date}</li>
                    <li>Changed By: {self.changed_by}</li>
                </ul>
                <p>Change Details:</p>
                <p>{self.change_summary}</p>
                <p>Reason: {self.change_reason}</p>
            """
            
            frappe.sendmail(
                recipients=list(set(recipients)),
                subject=subject,
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
    
    @frappe.whitelist()
    def revert_change(self):
        """Revert this change if possible"""
        if not frappe.has_permission("Family History", "write"):
            frappe.throw(_("Not permitted to revert changes"))
            
        member = frappe.get_doc("Church Member", self.member)
        
        if self.change_type == "Role Change" and self.old_family_role:
            member.family_role = self.old_family_role
            
        elif self.change_type == "Status Change" and self.old_family_status:
            member.family_status = self.old_family_status
            
        elif self.change_type == "Primary Contact Change":
            member.family_primary_contact = self.old_primary_contact
        
        if member.has_permission("write"):
            member.save()
            frappe.msgprint(_("Change reverted successfully"))
