import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr

class MinistrySegment(Document):
    def validate(self):
        self.validate_rules()
        self.build_member_query()
    
    def validate_rules(self):
        """Validate segmentation rules"""
        if not self.rules:
            frappe.throw(_("At least one segmentation rule is required"))
            
        for rule in self.rules:
            if rule.rule_type == "Demographics":
                self.validate_demographics_rule(rule)
            elif rule.rule_type == "Family Status":
                self.validate_family_status_rule(rule)
            elif rule.rule_type == "Ministry Involvement":
                self.validate_ministry_rule(rule)
            elif rule.rule_type == "Attendance":
                self.validate_attendance_rule(rule)
    
    def validate_demographics_rule(self, rule):
        """Validate demographics-based rules"""
        valid_conditions = [
            "age_greater_than", "age_less_than",
            "gender_is", "marital_status_is",
            "location_is"
        ]
        if rule.condition not in valid_conditions:
            frappe.throw(_(f"Invalid condition for Demographics: {rule.condition}"))
    
    def validate_family_status_rule(self, rule):
        """Validate family status rules"""
        valid_conditions = [
            "family_role_is", "has_children",
            "family_size_greater_than", "family_size_less_than",
            "is_primary_contact"
        ]
        if rule.condition not in valid_conditions:
            frappe.throw(_(f"Invalid condition for Family Status: {rule.condition}"))
    
    def validate_ministry_rule(self, rule):
        """Validate ministry involvement rules"""
        valid_conditions = [
            "has_role", "in_ministry",
            "leads_ministry", "volunteers_in"
        ]
        if rule.condition not in valid_conditions:
            frappe.throw(_(f"Invalid condition for Ministry Involvement: {rule.condition}"))
    
    def validate_attendance_rule(self, rule):
        """Validate attendance rules"""
        valid_conditions = [
            "attended_last_n_services",
            "attendance_rate_above",
            "attendance_rate_below",
            "missed_n_consecutive"
        ]
        if rule.condition not in valid_conditions:
            frappe.throw(_(f"Invalid condition for Attendance: {rule.condition}"))
    
    def build_member_query(self):
        """Build SQL query based on segmentation rules"""
        conditions = []
        params = {}
        
        for rule in self.rules:
            condition, rule_params = self.get_rule_condition(rule)
            if condition:
                conditions.append(condition)
                params.update(rule_params)
        
        if conditions:
            self.query_builder = f"""
                SELECT 
                    cm.name,
                    cm.first_name,
                    cm.last_name,
                    cm.email,
                    cm.phone
                FROM 
                    `tabChurch Member` cm
                WHERE 
                    cm.status = 'Active'
                    AND {" AND ".join(conditions)}
            """
            self.query_params = frappe.as_json(params)
    
    def get_rule_condition(self, rule):
        """Get SQL condition for a rule"""
        if rule.rule_type == "Demographics":
            return self.get_demographics_condition(rule)
        elif rule.rule_type == "Family Status":
            return self.get_family_status_condition(rule)
        elif rule.rule_type == "Ministry Involvement":
            return self.get_ministry_condition(rule)
        elif rule.rule_type == "Attendance":
            return self.get_attendance_condition(rule)
        return "", {}
    
    def get_demographics_condition(self, rule):
        """Get demographics-based conditions"""
        if rule.condition == "age_greater_than":
            return "TIMESTAMPDIFF(YEAR, cm.date_of_birth, CURDATE()) > %(age)s", {"age": cstr(rule.value)}
        elif rule.condition == "age_less_than":
            return "TIMESTAMPDIFF(YEAR, cm.date_of_birth, CURDATE()) < %(age)s", {"age": cstr(rule.value)}
        elif rule.condition == "gender_is":
            return "cm.gender = %(gender)s", {"gender": rule.value}
        return "", {}
    
    def get_family_status_condition(self, rule):
        """Get family status conditions"""
        if rule.condition == "family_role_is":
            return "cm.family_role = %(role)s", {"role": rule.value}
        elif rule.condition == "has_children":
            return """EXISTS (
                SELECT 1 FROM `tabChurch Member` child 
                WHERE child.family_unit = cm.family_unit 
                AND child.family_role = 'Child'
            )""", {}
        return "", {}
    
    def get_ministry_condition(self, rule):
        """Get ministry involvement conditions"""
        if rule.condition == "has_role":
            return """EXISTS (
                SELECT 1 FROM `tabChurch Ministry Role` role
                WHERE role.parent = cm.name 
                AND role.role = %(role)s
            )""", {"role": rule.value}
        return "", {}
    
    def get_attendance_condition(self, rule):
        """Get attendance-based conditions"""
        if rule.condition == "attendance_rate_above":
            return """(
                SELECT COUNT(*) / (
                    SELECT COUNT(*) FROM `tabChurch Service`
                    WHERE date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
                )
                FROM `tabChurch Attendance Detail` att
                WHERE att.member = cm.name
                AND att.parent IN (
                    SELECT name FROM `tabChurch Service`
                    WHERE date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
                )
            ) > %(rate)s""", {"rate": float(rule.value) / 100}
        return "", {}
    
    @frappe.whitelist()
    def preview_matching_members(self):
        """Preview members matching the segment criteria"""
        if not self.query_builder:
            return []
            
        params = frappe.parse_json(self.query_params or "{}")
        members = frappe.db.sql(self.query_builder, params, as_dict=1)
        
        return [{
            "name": member.name,
            "full_name": f"{member.first_name} {member.last_name}",
            "email": member.email,
            "phone": member.phone
        } for member in members]
    
    def send_communication(self, subject, message, communication_type="Email"):
        """Send communication to segment members"""
        if not self.is_active:
            frappe.throw(_("Cannot send communications for inactive segments"))
            
        members = self.preview_matching_members()
        
        if communication_type == "Email" and self.enable_email_notifications:
            self.send_email_communication(members, subject, message)
        elif communication_type == "SMS" and self.enable_sms_notifications:
            self.send_sms_communication(members, message)
        elif communication_type == "WhatsApp" and self.enable_whatsapp_notifications:
            self.send_whatsapp_communication(members, message)
    
    def send_email_communication(self, members, subject, message):
        """Send email to segment members"""
        for member in members:
            if member.email:
                frappe.sendmail(
                    recipients=[member.email],
                    subject=subject,
                    message=message,
                    reference_doctype=self.doctype,
                    reference_name=self.name
                )
    
    def send_sms_communication(self, members, message):
        """Send SMS to segment members"""
        # Implement SMS sending logic based on your SMS gateway
        pass
    
    def send_whatsapp_communication(self, members, message):
        """Send WhatsApp message to segment members"""
        # Implement WhatsApp sending logic based on your WhatsApp integration
        pass
