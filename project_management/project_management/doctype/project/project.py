import frappe
from frappe.model.document import Document

class Project(Document):
    """Custom controller for Project DocType."""

    def before_save(self):
        """Update calculated fields before each save."""
        # Count deliverables
        self.deliverable_count = len(self.get("deliverables"))

        # Sum paid reworks inside child rows, if the field exists
        self.correction_count = 0
        for d in self.get("deliverables"):
            if d.get("paid_rework"):
                self.correction_count += 1

        # Pricing fetched from the singleton settings DocType
        poster_price = frappe.db.get_single_value("PM Settings", "poster_price") or 0
        correction_price = frappe.db.get_single_value("PM Settings", "correction_price") or 0

        # Compute grand total
        self.grand_total = self.deliverable_count * poster_price + self.correction_count * correction_price 