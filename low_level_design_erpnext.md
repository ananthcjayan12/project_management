# Low-Level Design: Project Management App using ERPNext

## Overview
This document outlines the technical implementation of a project management application using ERPNext framework, based on the provided requirements.

## 1. Custom DocTypes Structure

### 1.1 Project Management (PM_Project)
```python
# Extends standard Project doctype
{
    "doctype": "PM_Project",
    "fields": [
        {"fieldname": "project_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "priority", "fieldtype": "Select", "options": "High\nMedium\nLow"},
        {"fieldname": "company_name", "fieldtype": "Link", "options": "Company"},
        {"fieldname": "client", "fieldtype": "Link", "options": "Customer"},
        {"fieldname": "due_date", "fieldtype": "Date", "reqd": 1},
        {"fieldname": "account_manager", "fieldtype": "Link", "options": "User"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nActive\nOn Hold\nCompleted\nCancelled"},
        {"fieldname": "total_financial", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "deliverables", "fieldtype": "Table", "options": "PM_Deliverable"},
        {"fieldname": "attachments", "fieldtype": "Table", "options": "PM_Attachment"}
    ]
}
```

### 1.2 Deliverable (PM_Deliverable)
```python
{
    "doctype": "PM_Deliverable",
    "fields": [
        {"fieldname": "deliverable_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "deliverable_type", "fieldtype": "Select", "options": "Poster\nBanner\nLogo\nBrochure\nWebsite\nOther"},
        {"fieldname": "count", "fieldtype": "Int", "default": 1},
        {"fieldname": "unit_price", "fieldtype": "Currency"},
        {"fieldname": "total_price", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "status", "fieldtype": "Select", "options": "Action Pending\nIn Progress\nClient Review\nCompleted"},
        {"fieldname": "assigned_to", "fieldtype": "Link", "options": "User"},
        {"fieldname": "original_eta", "fieldtype": "Date"},
        {"fieldname": "designer_eta", "fieldtype": "Date"},
        {"fieldname": "creative_director", "fieldtype": "Link", "options": "User"},
        {"fieldname": "designer", "fieldtype": "Link", "options": "User"},
        {"fieldname": "points", "fieldtype": "Int", "default": 1},
        {"fieldname": "correction_count", "fieldtype": "Int", "default": 0},
        {"fieldname": "correction_amount", "fieldtype": "Currency", "default": 0},
        {"fieldname": "tags", "fieldtype": "Table MultiSelect", "options": "PM_Tag"}
    ]
}
```

### 1.3 Task Management (PM_Task)
```python
{
    "doctype": "PM_Task",
    "fields": [
        {"fieldname": "task_id", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "project", "fieldtype": "Link", "options": "PM_Project"},
        {"fieldname": "deliverable", "fieldtype": "Link", "options": "PM_Deliverable"},
        {"fieldname": "task_type", "fieldtype": "Select", "options": "Design\nQC Review\nClient Review\nRework"},
        {"fieldname": "status", "fieldtype": "Select", "options": "To Do\nIn Progress\nUnder Review\nCompleted\nRejected"},
        {"fieldname": "assigned_to", "fieldtype": "Link", "options": "User"},
        {"fieldname": "assigned_by", "fieldtype": "Link", "options": "User"},
        {"fieldname": "priority", "fieldtype": "Select", "options": "High\nMedium\nLow"},
        {"fieldname": "due_date", "fieldtype": "Datetime"},
        {"fieldname": "description", "fieldtype": "Text Editor"},
        {"fieldname": "rework_reason", "fieldtype": "Text Editor"},
        {"fieldname": "is_paid_rework", "fieldtype": "Check", "default": 0},
        {"fieldname": "is_complementary", "fieldtype": "Check", "default": 0},
        {"fieldname": "files", "fieldtype": "Table", "options": "PM_File_Version"}
    ]
}
```

### 1.4 File Version Management (PM_File_Version)
```python
{
    "doctype": "PM_File_Version",
    "fields": [
        {"fieldname": "version_number", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "file_name", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "file_url", "fieldtype": "Attach"},
        {"fieldname": "file_type", "fieldtype": "Select", "options": "Image\nDocument\nVideo\nOther"},
        {"fieldname": "uploaded_by", "fieldtype": "Link", "options": "User"},
        {"fieldname": "upload_date", "fieldtype": "Datetime"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nSubmitted\nApproved\nRejected"},
        {"fieldname": "feedback", "fieldtype": "Text Editor"},
        {"fieldname": "is_preview_available", "fieldtype": "Check", "default": 0}
    ]
}
```

### 1.5 QC Review (PM_QC_Review)
```python
{
    "doctype": "PM_QC_Review",
    "fields": [
        {"fieldname": "task", "fieldtype": "Link", "options": "PM_Task"},
        {"fieldname": "reviewer", "fieldtype": "Link", "options": "User"},
        {"fieldname": "review_date", "fieldtype": "Datetime"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Pending\nApproved\nRejected"},
        {"fieldname": "feedback", "fieldtype": "Text Editor"},
        {"fieldname": "checklist", "fieldtype": "Table", "options": "PM_QC_Checklist"}
    ]
}
```

## 2. Custom Workflows

### 2.1 Task Workflow
```python
# workflows/task_workflow.py
task_workflow = {
    "workflow_name": "PM Task Workflow",
    "document_type": "PM_Task",
    "workflow_state_field": "status",
    "states": [
        {"state": "To Do", "allow_edit": "Designer"},
        {"state": "In Progress", "allow_edit": "Designer"},
        {"state": "QC Review", "allow_edit": "QC Reviewer"},
        {"state": "Client Review", "allow_edit": "Account Manager"},
        {"state": "Completed", "allow_edit": "None"},
        {"state": "Rejected", "allow_edit": "Designer"}
    ],
    "transitions": [
        {"state": "To Do", "action": "Start", "next_state": "In Progress", "allowed": "Designer"},
        {"state": "In Progress", "action": "Submit for QC", "next_state": "QC Review", "allowed": "Designer"},
        {"state": "QC Review", "action": "Approve", "next_state": "Client Review", "allowed": "QC Reviewer"},
        {"state": "QC Review", "action": "Reject", "next_state": "Rejected", "allowed": "QC Reviewer"},
        {"state": "Client Review", "action": "Approve", "next_state": "Completed", "allowed": "Account Manager"},
        {"state": "Client Review", "action": "Request Rework", "next_state": "To Do", "allowed": "Account Manager"},
        {"state": "Rejected", "action": "Rework", "next_state": "In Progress", "allowed": "Designer"}
    ]
}
```

## 3. Custom Dashboards

### 3.1 Account Manager Dashboard
```python
# dashboards/account_manager_dashboard.py
class AccountManagerDashboard:
    def get_dashboard_data(self):
        return {
            "cards": [
                {
                    "card_name": "Total Projects",
                    "value": self.get_total_projects(),
                    "color": "blue"
                },
                {
                    "card_name": "Active Clients",
                    "value": self.get_active_clients(),
                    "color": "green"
                },
                {
                    "card_name": "Pending Deliverables",
                    "value": self.get_pending_deliverables(),
                    "color": "orange"
                },
                {
                    "card_name": "Unassigned Tasks",
                    "value": self.get_unassigned_tasks(),
                    "color": "red"
                }
            ],
            "charts": [
                {
                    "chart_name": "Project Status Distribution",
                    "chart_type": "donut",
                    "data": self.get_project_status_data()
                }
            ]
        }
```

### 3.2 Creative Director Dashboard
```python
# dashboards/creative_director_dashboard.py
class CreativeDirectorDashboard:
    def get_dashboard_data(self):
        return {
            "cards": [
                {
                    "card_name": "Unassigned Deliverables",
                    "value": self.get_unassigned_deliverables(),
                    "color": "blue"
                },
                {
                    "card_name": "Team Deliverables",
                    "value": self.get_team_deliverables(),
                    "color": "green"
                },
                {
                    "card_name": "Overdue Tasks",
                    "value": self.get_overdue_tasks(),
                    "color": "red"
                }
            ],
            "charts": [
                {
                    "chart_name": "Designer Workload",
                    "chart_type": "bar",
                    "data": self.get_designer_workload()
                }
            ]
        }
```

## 4. Kanban Board Implementation

### 4.1 Custom Kanban View
```python
# kanban/kanban_view.py
class PMKanbanView:
    def __init__(self, user_role):
        self.user_role = user_role
        self.columns = self.get_columns_by_role()
    
    def get_columns_by_role(self):
        if self.user_role == "Account Manager":
            return ["Action Pending", "In Progress", "Client Review", "Completed"]
        elif self.user_role == "Creative Director":
            return ["To Do", "In Progress", "Team Tasks Over Due", "Waiting for Client Approval"]
        elif self.user_role == "Designer":
            return ["To Do", "In Progress"]
        elif self.user_role == "Client":
            return ["Pending Approval", "Revision in Progress", "Approved Design"]
        elif self.user_role == "QC Reviewer":
            return ["Pending Reviews", "In Review", "Completed Reviews"]
    
    def get_tasks_by_column(self, column):
        # Implementation to fetch tasks based on column and user role
        pass
```

## 5. Permission Structure

### 5.1 Role-based Permissions
```python
# permissions/role_permissions.py
role_permissions = {
    "Account Manager": {
        "PM_Project": ["read", "write", "create", "delete"],
        "PM_Task": ["read", "write", "create"],
        "PM_Deliverable": ["read", "write", "create"],
        "Customer": ["read", "write", "create"]
    },
    "Creative Director": {
        "PM_Task": ["read", "write"],
        "PM_Deliverable": ["read", "write"],
        "User": ["read"]  # For assignment purposes
    },
    "Designer": {
        "PM_Task": ["read", "write"],  # Only assigned tasks
        "PM_File_Version": ["read", "write", "create"]
    },
    "QC Reviewer": {
        "PM_Task": ["read", "write"],  # Only QC tasks
        "PM_QC_Review": ["read", "write", "create"],
        "PM_File_Version": ["read"]
    },
    "Client": {
        "PM_Task": ["read"],  # Only client review tasks
        "PM_File_Version": ["read"]
    }
}
```

## 6. API Endpoints

### 6.1 REST API Structure
```python
# api/project_management.py
@frappe.whitelist()
def assign_task(task_id, assigned_to, assigned_by):
    """Assign task to user"""
    pass

@frappe.whitelist()
def submit_design(task_id, file_data):
    """Submit design for review"""
    pass

@frappe.whitelist()
def approve_task(task_id, feedback=""):
    """Approve task"""
    pass

@frappe.whitelist()
def request_rework(task_id, feedback, is_paid=False):
    """Request rework on task"""
    pass

@frappe.whitelist()
def get_dashboard_data(user_role):
    """Get dashboard data based on user role"""
    pass

@frappe.whitelist()
def get_kanban_data(user_role, filters=None):
    """Get kanban board data"""
    pass
```

## 7. Financial Calculations

### 7.1 Financial Calculation Logic
```python
# financial/calculations.py
class FinancialCalculator:
    def calculate_total_financial(self, project_id):
        """
        Formula: Total Financial = (m * X) + (n * y)
        where:
        m = deliverable count
        X = unit price per deliverable
        n = correction count (payable)
        y = correction amount
        """
        project = frappe.get_doc("PM_Project", project_id)
        total = 0
        
        for deliverable in project.deliverables:
            # Base deliverable cost
            base_cost = deliverable.count * deliverable.unit_price
            
            # Correction costs (only payable corrections)
            correction_cost = deliverable.correction_count * deliverable.correction_amount
            
            total += base_cost + correction_cost
        
        return total
```

## 8. File Management Integration

### 8.1 Google Drive Integration
```python
# integrations/google_drive.py
class GoogleDriveIntegration:
    def __init__(self):
        self.drive_service = self.authenticate_drive()
    
    def upload_file(self, file_path, folder_id):
        """Upload file to Google Drive"""
        pass
    
    def create_project_folder(self, project_name):
        """Create project folder in Google Drive"""
        pass
    
    def get_file_preview_url(self, file_id):
        """Get preview URL for file"""
        pass
```

## 9. Chat/Communication System

### 9.1 Real-time Communication
```python
# communication/chat_system.py
class ChatSystem:
    def __init__(self):
        self.socket_io = frappe.socketio
    
    def send_message(self, task_id, sender, message):
        """Send message in task chat"""
        pass
    
    def notify_user(self, user_id, notification_type, data):
        """Send real-time notification"""
        pass
```

## 10. Implementation Steps

### Phase 1: Core Setup
1. Install ERPNext
2. Create custom DocTypes
3. Set up basic workflows
4. Implement role-based permissions
5. Create basic dashboards

### Phase 2: Advanced Features
1. Implement Kanban boards
2. Set up file management
3. Create API endpoints
4. Implement financial calculations
5. Add real-time communication

### Phase 3: Integrations
1. Google Drive integration
2. Email notifications
3. Mobile app APIs
4. Third-party tool integrations

### Phase 4: Advanced Features
1. AI-powered features (plagiarism detection)
2. Advanced analytics
3. Performance optimization
4. Security enhancements

## 11. Database Schema Considerations

### 11.1 Index Strategy
```sql
-- Key indexes for performance
CREATE INDEX idx_pm_task_assigned_to ON `tabPM_Task`(assigned_to);
CREATE INDEX idx_pm_task_status ON `tabPM_Task`(status);
CREATE INDEX idx_pm_task_due_date ON `tabPM_Task`(due_date);
CREATE INDEX idx_pm_project_client ON `tabPM_Project`(client);
```

### 11.2 Backup Strategy
- Daily automated backups
- File storage backup integration
- Version history preservation

## 12. Security Considerations

### 12.1 Data Protection
- Role-based access control
- Field-level permissions
- API rate limiting
- File access controls
- Audit trail logging

## 13. Testing Strategy

### 13.1 Test Cases
- Unit tests for each DocType
- Workflow testing
- Permission testing
- API endpoint testing
- Integration testing
- Performance testing

---

# STEP-BY-STEP IMPLEMENTATION TUTORIAL

## Prerequisites
- Ubuntu/Debian server or local machine
- Python 3.8+ installed
- Node.js 14+ installed
- MariaDB/MySQL installed
- Basic knowledge of Python and JavaScript

## Step 1: ERPNext Installation

### 1.1 Install System Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-dev python3-pip python3-venv
sudo apt install nodejs npm
sudo apt install redis-server
sudo apt install mariadb-server mariadb-client
sudo apt install git curl
sudo apt install wkhtmltopdf

# Install yarn
sudo npm install -g yarn
```

### 1.2 Install Frappe Bench
```bash
# Install bench
sudo pip3 install frappe-bench

# Create a new bench
bench init --frappe-branch version-14 frappe-bench
cd frappe-bench

# Create a new site
bench new-site pm-site.local --admin-password admin123
```

### 1.3 Install ERPNext
```bash
# Get ERPNext app
bench get-app --branch version-14 erpnext

# Install ERPNext on your site
bench --site pm-site.local install-app erpnext

# Start the development server
bench start
```

## Step 2: Create Custom App

### 2.1 Create New App
```bash
# Create custom app
bench new-app project_management

# Install the app on site
bench --site pm-site.local install-app project_management
```

### 2.2 App Structure
Your app will be created in `apps/project_management/` with this structure:
```
project_management/
├── project_management/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   └── project_management/
│       ├── __init__.py
│       ├── doctype/
│       ├── page/
│       ├── report/
│       └── workspace/
├── requirements.txt
└── setup.py
```

## Step 3: Create Custom DocTypes

### 3.1 Create PM_Project DocType

Navigate to your ERPNext instance and go to:
**Setup > Customization > DocType > New**

Or use bench command:
```bash
bench --site pm-site.local execute frappe.core.doctype.doctype.doctype.create_doctype
```

Create `pm_project.json` in `apps/project_management/project_management/project_management/doctype/pm_project/`:

```json
{
    "doctype": "DocType",
    "name": "PM Project",
    "module": "Project Management",
    "custom": 1,
    "fields": [
        {
            "fieldname": "project_name",
            "label": "Project Name",
            "fieldtype": "Data",
            "reqd": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "priority",
            "label": "Priority",
            "fieldtype": "Select",
            "options": "High\nMedium\nLow",
            "default": "Medium"
        },
        {
            "fieldname": "company_name",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company"
        },
        {
            "fieldname": "client",
            "label": "Client",
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 1
        },
        {
            "fieldname": "due_date",
            "label": "Due Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "account_manager",
            "label": "Account Manager",
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": "Draft\nActive\nOn Hold\nCompleted\nCancelled",
            "default": "Draft"
        },
        {
            "fieldname": "total_financial",
            "label": "Total Financial",
            "fieldtype": "Currency",
            "read_only": 1
        },
        {
            "fieldname": "deliverables_section",
            "label": "Deliverables",
            "fieldtype": "Section Break"
        },
        {
            "fieldname": "deliverables",
            "label": "Deliverables",
            "fieldtype": "Table",
            "options": "PM Deliverable"
        }
    ],
    "permissions": [
        {
            "role": "Account Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1
        }
    ]
}
```

### 3.2 Create the DocType Python File

Create `pm_project.py` in the same directory:

```python
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PMProject(Document):
    def validate(self):
        self.calculate_total_financial()
    
    def calculate_total_financial(self):
        """Calculate total financial based on deliverables"""
        total = 0
        for deliverable in self.deliverables:
            if deliverable.count and deliverable.unit_price:
                base_cost = deliverable.count * deliverable.unit_price
                correction_cost = (deliverable.correction_count or 0) * (deliverable.correction_amount or 0)
                total += base_cost + correction_cost
        
        self.total_financial = total
```

### 3.3 Create Child DocType (PM_Deliverable)

Create similar files for `PM Deliverable`:

`pm_deliverable.json`:
```json
{
    "doctype": "DocType",
    "name": "PM Deliverable",
    "module": "Project Management",
    "custom": 1,
    "istable": 1,
    "fields": [
        {
            "fieldname": "deliverable_name",
            "label": "Deliverable Name",
            "fieldtype": "Data",
            "reqd": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "deliverable_type",
            "label": "Type",
            "fieldtype": "Select",
            "options": "Poster\nBanner\nLogo\nBrochure\nWebsite\nOther",
            "in_list_view": 1
        },
        {
            "fieldname": "count",
            "label": "Count",
            "fieldtype": "Int",
            "default": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "unit_price",
            "label": "Unit Price",
            "fieldtype": "Currency",
            "in_list_view": 1
        },
        {
            "fieldname": "total_price",
            "label": "Total Price",
            "fieldtype": "Currency",
            "read_only": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": "Action Pending\nIn Progress\nClient Review\nCompleted",
            "default": "Action Pending"
        },
        {
            "fieldname": "designer",
            "label": "Designer",
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "points",
            "label": "Points",
            "fieldtype": "Int",
            "default": 1
        }
    ]
}
```

## Step 4: Create Roles and Permissions

### 4.1 Create Custom Roles
Go to **Setup > Users and Permissions > Role > New**

Create these roles:
- Account Manager
- Creative Director  
- Designer
- QC Reviewer

### 4.2 Set Up Role Permissions
Go to **Setup > Users and Permissions > Role Permissions Manager**

For each DocType, set permissions according to the design:

```python
# Script to set permissions programmatically
import frappe

def setup_permissions():
    # PM Project permissions
    frappe.permissions.add_permission("PM Project", "Account Manager", 0)
    frappe.permissions.update_permission("PM Project", "Account Manager", 0, "read", 1)
    frappe.permissions.update_permission("PM Project", "Account Manager", 0, "write", 1)
    frappe.permissions.update_permission("PM Project", "Account Manager", 0, "create", 1)
    frappe.permissions.update_permission("PM Project", "Account Manager", 0, "delete", 1)
    
    # Add similar permissions for other roles
    
setup_permissions()
```

## Step 5: Create Workflows

### 5.1 Create Task Workflow
Go to **Setup > Workflow > New**

Create workflow with these details:
- **Document Type**: PM Task
- **Workflow Name**: PM Task Workflow
- **Workflow State Field**: status

**States**:
1. To Do (Allow editing: Designer)
2. In Progress (Allow editing: Designer)
3. QC Review (Allow editing: QC Reviewer)
4. Client Review (Allow editing: Account Manager)
5. Completed (Allow editing: None)
6. Rejected (Allow editing: Designer)

**Transitions**:
- To Do → In Progress (Action: Start, Allowed: Designer)
- In Progress → QC Review (Action: Submit for QC, Allowed: Designer)
- QC Review → Client Review (Action: Approve, Allowed: QC Reviewer)
- QC Review → Rejected (Action: Reject, Allowed: QC Reviewer)
- Client Review → Completed (Action: Approve, Allowed: Account Manager)
- Client Review → To Do (Action: Request Rework, Allowed: Account Manager)

## Step 6: Create Custom Pages and Dashboards

### 6.1 Create Dashboard Page
Create `account_manager_dashboard.py` in `apps/project_management/project_management/project_management/page/`:

```python
import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_data():
    data = {
        "cards": [
            {
                "name": "Total Projects",
                "value": frappe.db.count("PM Project"),
                "color": "blue"
            },
            {
                "name": "Active Projects", 
                "value": frappe.db.count("PM Project", {"status": "Active"}),
                "color": "green"
            },
            {
                "name": "Pending Tasks",
                "value": frappe.db.count("PM Task", {"status": ["in", ["To Do", "In Progress"]]}),
                "color": "orange"
            }
        ]
    }
    return data
```

### 6.2 Create Dashboard HTML
Create `account_manager_dashboard.html`:

```html
<div class="dashboard-container">
    <div class="row">
        <div class="col-md-3" v-for="card in cards">
            <div class="card text-center" :class="'border-' + card.color">
                <div class="card-body">
                    <h2 :class="'text-' + card.color">{{ card.value }}</h2>
                    <p class="card-text">{{ card.name }}</p>
                </div>
            </div>
        </div>
    </div>
</div>
```

## Step 7: Create Kanban Board

### 7.1 Create Custom Kanban View
Create `kanban_board.js`:

```javascript
frappe.pages['kanban-board'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Project Kanban Board',
        single_column: true
    });
    
    frappe.kanban_board = new KanbanBoard(page);
};

class KanbanBoard {
    constructor(page) {
        this.page = page;
        this.setup();
    }
    
    setup() {
        this.get_user_role().then(role => {
            this.user_role = role;
            this.setup_columns();
            this.load_tasks();
        });
    }
    
    get_user_role() {
        return frappe.call({
            method: 'project_management.api.get_user_role'
        }).then(r => r.message);
    }
    
    setup_columns() {
        const columns = this.get_columns_by_role();
        // Create kanban columns
        this.create_kanban_structure(columns);
    }
    
    get_columns_by_role() {
        const role_columns = {
            "Account Manager": ["Action Pending", "In Progress", "Client Review", "Completed"],
            "Creative Director": ["To Do", "In Progress", "Team Tasks Over Due", "Waiting for Client Approval"],
            "Designer": ["To Do", "In Progress"],
            "QC Reviewer": ["Pending Reviews", "In Review", "Completed Reviews"]
        };
        return role_columns[this.user_role] || [];
    }
}
```

## Step 8: Create API Endpoints

### 8.1 Create API File
Create `api.py` in your app root:

```python
import frappe
from frappe import _

@frappe.whitelist()
def assign_task(task_id, assigned_to, assigned_by):
    """Assign task to user"""
    try:
        task = frappe.get_doc("PM Task", task_id)
        task.assigned_to = assigned_to
        task.assigned_by = assigned_by
        task.save()
        
        # Send notification
        send_notification(assigned_to, f"New task assigned: {task.task_id}")
        
        return {"status": "success", "message": "Task assigned successfully"}
    except Exception as e:
        frappe.log_error(str(e))
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def submit_design(task_id, file_data):
    """Submit design for review"""
    try:
        task = frappe.get_doc("PM Task", task_id)
        
        # Create file version
        file_version = frappe.get_doc({
            "doctype": "PM File Version",
            "task": task_id,
            "version_number": get_next_version(task_id),
            "file_name": file_data.get("file_name"),
            "file_url": file_data.get("file_url"),
            "uploaded_by": frappe.session.user,
            "status": "Submitted"
        })
        file_version.insert()
        
        # Update task status
        task.status = "QC Review"
        task.save()
        
        return {"status": "success", "message": "Design submitted for review"}
    except Exception as e:
        frappe.log_error(str(e))
        return {"status": "error", "message": str(e)}

def get_next_version(task_id):
    """Get next version number for task"""
    last_version = frappe.db.sql("""
        SELECT version_number 
        FROM `tabPM File Version` 
        WHERE task = %s 
        ORDER BY creation DESC 
        LIMIT 1
    """, task_id)
    
    if last_version:
        return f"v{int(last_version[0][0][1:]) + 1}"
    return "v1"

def send_notification(user, message):
    """Send notification to user"""
    frappe.publish_realtime(
        event="task_notification",
        message={"message": message},
        user=user
    )
```

## Step 9: Set Up File Management

### 9.1 Configure File Storage
In `hooks.py`, add:

```python
# File storage configuration
boot_session = "project_management.boot.boot_session"

# Custom file upload handler
upload_to_drive = "project_management.integrations.google_drive.upload_to_drive"
```

### 9.2 Google Drive Integration
Create `integrations/google_drive.py`:

```python
import frappe
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GoogleDriveIntegration:
    def __init__(self):
        self.service = self.get_drive_service()
    
    def get_drive_service(self):
        """Initialize Google Drive service"""
        # Load credentials from ERPNext settings
        creds_data = frappe.get_single("Google Drive Settings")
        creds = Credentials.from_authorized_user_info(creds_data.credentials)
        return build('drive', 'v3', credentials=creds)
    
    def upload_file(self, file_path, folder_id=None):
        """Upload file to Google Drive"""
        try:
            file_metadata = {
                'name': file_path.split('/')[-1],
                'parents': [folder_id] if folder_id else []
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except Exception as e:
            frappe.log_error(str(e))
            return None
    
    def create_project_folder(self, project_name):
        """Create folder for project"""
        try:
            folder_metadata = {
                'name': f"Project_{project_name}",
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
        except Exception as e:
            frappe.log_error(str(e))
            return None
```

## Step 10: Testing and Deployment

### 10.1 Run Migration
```bash
# Migrate DocTypes
bench --site pm-site.local migrate

# Clear cache
bench --site pm-site.local clear-cache

# Restart
bench restart
```

### 10.2 Create Test Data
Create a script to generate test data:

```python
# test_data.py
import frappe

def create_test_data():
    # Create test client
    if not frappe.db.exists("Customer", "Test Client"):
        client = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Test Client",
            "customer_type": "Company"
        })
        client.insert()
    
    # Create test project
    project = frappe.get_doc({
        "doctype": "PM Project",
        "project_name": "Test Project 1",
        "client": "Test Client",
        "due_date": "2024-12-31",
        "priority": "High",
        "deliverables": [
            {
                "deliverable_name": "Logo Design",
                "deliverable_type": "Logo",
                "count": 1,
                "unit_price": 500
            },
            {
                "deliverable_name": "Business Card",
                "deliverable_type": "Other",
                "count": 2,
                "unit_price": 100
            }
        ]
    })
    project.insert()
    
    print("Test data created successfully!")

# Run this in ERPNext console
create_test_data()
```

### 10.3 Performance Testing
Create performance test scripts:

```python
# performance_test.py
import frappe
import time

def test_dashboard_performance():
    start_time = time.time()
    
    # Test dashboard data loading
    data = frappe.call("project_management.api.get_dashboard_data", user_role="Account Manager")
    
    end_time = time.time()
    print(f"Dashboard loaded in {end_time - start_time:.2f} seconds")

def test_kanban_performance():
    start_time = time.time()
    
    # Test kanban data loading
    data = frappe.call("project_management.api.get_kanban_data", user_role="Designer")
    
    end_time = time.time()
    print(f"Kanban loaded in {end_time - start_time:.2f} seconds")
```

## Step 11: Production Deployment

### 11.1 Production Setup
```bash
# Setup production
sudo bench setup production $(whoami)

# Enable scheduler
bench --site pm-site.local enable-scheduler

# Setup SSL (optional)
sudo bench setup lets-encrypt pm-site.local

# Setup backup
bench --site pm-site.local backup --with-files
```

### 11.2 Monitoring Setup
Create monitoring scripts:

```python
# monitoring.py
import frappe
from frappe.utils import now

def log_system_health():
    """Log system health metrics"""
    health_data = {
        "timestamp": now(),
        "active_users": len(frappe.get_active_users()),
        "total_projects": frappe.db.count("PM Project"),
        "pending_tasks": frappe.db.count("PM Task", {"status": ["!=", "Completed"]})
    }
    
    # Log to system
    frappe.log_error(str(health_data), "System Health")
```

## Troubleshooting Guide

### Common Issues:

1. **Migration Errors**
```bash
# Fix migration issues
bench --site pm-site.local migrate --skip-failing
bench --site pm-site.local reload-doctype "PM Project"
```

2. **Permission Issues**
```bash
# Reset permissions
bench --site pm-site.local execute frappe.permissions.reset_perms
```

3. **JavaScript Errors**
```bash
# Clear cache and rebuild
bench --site pm-site.local clear-cache
bench build
```

4. **Database Issues**
```bash
# Check database connectivity
bench --site pm-site.local mariadb
```

## Next Steps

1. **Phase 2 Implementation**: Add advanced Kanban features
2. **Mobile App**: Create mobile interface using Frappe's mobile framework
3. **Analytics**: Implement advanced reporting
4. **AI Integration**: Add plagiarism detection and smart suggestions

This comprehensive tutorial provides your developers with everything they need to implement the project management system using ERPNext, even if they're new to the framework.

This low-level design provides a comprehensive framework for implementing the project management application using ERPNext. Developers can follow this structure to build a robust, scalable solution that meets all the specified requirements. 