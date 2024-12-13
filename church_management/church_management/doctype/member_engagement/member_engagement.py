# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from typing import List, Dict
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, validate_date
from frappe import _

class MemberEngagement(Document):
    """
    Member Engagement tracks and scores various types of member participation in church activities.
    
    The engagement score is calculated based on:
    1. Base score for the type of engagement:
       - Attendance: 1 point
       - Ministry: 3 points
       - Event: 2 points
       - Small Group: 2 points
    2. Duration multiplier: score * (1 + duration/2)
    
    Trend is calculated by comparing current score with average of last 3 engagements:
    - Increasing: >10% above average
    - Decreasing: >10% below average
    - Stable: within ±10% of average
    """
    
    def validate(self) -> None:
        """Validate document fields before save"""
        if self.date:
            validate_date(self.date)
            if getdate(self.date) > getdate(nowdate()):
                frappe.throw(_("Engagement date cannot be in the future"))
                
        if self.duration and self.duration < 0:
            frappe.throw(_("Duration cannot be negative"))
            
        valid_types = ["Attendance", "Ministry", "Event", "Small Group"]
        if self.engagement_type not in valid_types:
            frappe.throw(_("Invalid engagement type. Must be one of: {0}").format(
                ", ".join(valid_types)
            ))

    def before_save(self) -> None:
        """Update engagement metrics before saving"""
        self.last_update = nowdate()
        self.calculate_engagement_score()
        self.calculate_trend()
    
    def calculate_engagement_score(self) -> None:
        """Calculate engagement score based on type and duration"""
        base_scores: Dict[str, int] = {
            "Attendance": 1,
            "Ministry": 3,
            "Event": 2,
            "Small Group": 2
        }
        
        # Get base score for engagement type
        self.engagement_score = base_scores[self.engagement_type]
        
        # Apply duration multiplier if duration is provided
        if self.duration and self.duration > 0:
            self.engagement_score = int(self.engagement_score * (1 + self.duration/2))
    
    def calculate_trend(self) -> None:
        """Calculate engagement trend based on comparison with recent history"""
        previous_engagements = frappe.get_all(
            "Member Engagement",
            filters={
                "member": self.member,
                "date": ["<", self.date],
                "docstatus": 1  # Only consider submitted documents
            },
            fields=["engagement_score"],
            order_by="date desc",
            limit=3
        )
        
        if not previous_engagements:
            self.trend = "Stable"
            return
            
        total_score = sum(d.engagement_score for d in previous_engagements)
        avg_previous_score = total_score / len(previous_engagements)
        
        # Determine trend based on 10% threshold
        if self.engagement_score > avg_previous_score * 1.1:
            self.trend = "Increasing"
        elif self.engagement_score < avg_previous_score * 0.9:
            self.trend = "Decreasing"
        else:
            self.trend = "Stable"
