# 🔧 **Full-Stack Development Guide & Functional Walk-Through**  
### Project Management App (Frappe Framework)

This document turns `project_requirements.txt` into an exhaustive blueprint you can follow—from the first `bench init` all the way to production rollout and day-to-day usage.  It is cross-checked against the techniques shown in `frappe_tutorial_combined.txt`.

---
## CONTENTS
1. High-Level Overview & Glossary
2. Local Environment Setup  
3. Creating the Bench, Site & App  
4. Frappe Fundamentals Refresher  
5. Detailed Data-Model Design (DocTypes)  
6. Roles, Users & Permissions  
7. Workflows & Document Life-Cycles  
8. UI/UX: Kanban Boards, Dashboards & Workspaces  
9. Server-Side Logic (Python Controllers)  
10. Client-Side Enhancements (JS Form Scripts)  
11. Web Portal & Public Pages  
12. File Storage & External Integrations  
13. Automated Tests & Fixtures  
14. CI / CD & Code-Quality Tooling  
15. Deployment Options & Production Hardening  
16. **Operational Workflow Narrative** (real-life use-cases)  
17. Phase-2 Features & Backlog  

> You can jump directly to any heading in Desk ➞ *Help ▶ Search* by typing the section title.

---
## 1 · OVERVIEW & GLOSSARY
| Term | Meaning |
|------|---------|
| **Account Manager (AM)** | Customer-facing project owner; can create projects, assign tasks, request reworks. |
| **Creative Director (CD)** | Oversees designers and schedules work. |
| **Designer** | Creates design deliverables. |
| **QC Reviewer** | Performs quality checks before client review. |
| **Client User** | External user who approves or rejects deliverables. |
| **Deliverable** | A unit of work (poster, banner, etc.) belonging to a Project. |
| **Task** | A granular action card that moves through Kanban columns. |
| **Rework Log** | Side-record capturing paid/complimentary rework flags. |
| **PM Settings** | Singleton DocType storing poster/correction prices. |
| **Status** | Field driving both Workflows and Kanban columns. |

---
## 2 · LOCAL ENVIRONMENT SETUP
1. **Install dependencies** (macOS examples):
   ```bash
   brew install redis mariadb@10.6 node@16 yarn git pre-commit wget
   sudo gem install wkhtmltopdf
   ```
2. **Create and activate Python 3.10 virtualenv** *(Optional but recommended)*:
   ```bash
   python3.10 -m venv ~/.venvs/frappe
   source ~/.venvs/frappe/bin/activate
   ```
3. **Bench CLI** (v5+):
   ```bash
   pip install frappe-bench
   bench --version      # verify
   ```
4. **MariaDB tuning** *(only once)*: `mysql_secure_installation` → set root pwd.
5. **Pre-commit** (global): `pre-commit --version` ➞ should print a version.

Troubleshooting FAQ is identical to the one in the Frappe tutorial—refer there if Redis/MariaDB ports clash.

---
## 3 · BOOTSTRAPPING BENCH, SITE & APP
### 3.1 Create Bench Folder
```bash
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
```

### 3.2 Get the Custom App
(We already have `project_management` in Git; clone or add as a sub-module.)
```bash
bench get-app ../path/to/local/project_management
```
If the repo is on GitHub:
```bash
bench get-app project_management https://github.com/your-org/project_management.git --branch develop
```

### 3.3 Create Site & Install App
```bash
bench new-site proj.localhost    # set MariaDB root pwd & choose Admin pwd
bench --site proj.localhost install-app project_management
bench --site proj.localhost add-to-hosts
```

### 3.4 Enable Developer Mode
```bash
bench set-config -g developer_mode true
bench restart
```
> Developer mode allows bench to auto-generate controller files when you save a DocType.

### 3.5 Start the Multi-process Server (dev)
```bash
bench start
```
Open http://proj.localhost:8000 and log in as **Administrator**.

---
## 4 · FRAPPE FUNDAMENTALS REFRESHER (Quick)
| Concept | What it does | Where it appears |
|---------|--------------|------------------|
| DocType | Data-model + view + controller spec | *Developer ▶ DocType* |
| Child Table | Repeating rows inside a parent DocType | Field type *Table* |
| Workflow | State machine + permissions | *Settings ▶ Workflow* |
| Workspace | Custom dashboards | *Developer ▶ Workspace* |
| Web View | Public webpage for records | *DocType ▶ Web View section* |

The Library tutorial fully demonstrates CRUD, controller hooks and web views—refer back for screenshots if needed.

---
## 5 · DETAILED DATA-MODEL DESIGN
Below are **copy-paste-ready field matrices**. Create each DocType through Desk, then reload (⚙ ▶ Reload) to generate boiler-plate files.

> **Checkbox defaults:** Leave **Custom?** and **Is Virtual** unchecked for every DocType in this guide. They apply only to ad-hoc customizations or virtual/externally-backed tables, which we are not using here.

### 5.1 Client (Master)
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ❌
- Is Child Table: ❌
- Is Single: ❌
- Is Tree: ❌

| Label | Field-type | Options | Mandatory | Notes |
|-------|-----------|---------|-----------|-------|
| Client Name | Data | | ✅ | Title
| Company | Data | | | 
| Email | Data | Email | | 
| Active | Check | | | default=1

**Auto-name**: `field:client_name`  
**Has Web View**: Yes ➜ Route = `clients` ➜ Show "See on Website" link.

### 5.2 Project (Submittable)
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ✅
- Is Child Table: ❌
- Is Single: ❌
- Is Tree: ❌

| Label | Type | Options | Req |
|-------|------|---------|-----|
| Project Name | Data | | ✅ |
| Priority | Select | Low\nMedium\nHigh | ✅ |
| Client | Link | Client | ✅ |
| Due Date | Date | | ✅ |
| Deliverables | Table | Deliverable | |
| Attachments | Attach | | |
| Deliverable Count | Int | | Read Only |
| Correction Count | Int | | Read Only |
| Grand Total | Currency | | Read Only |
| Status | Select | Draft\nIn Progress\nClient Review\nCompleted\nRejected | |

Settings:
* **Is Submittable**: ✔︎  
* **Title Field**: `project_name`

### 5.3 Deliverable (Child Table)
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ❌
- Is Child Table: ✅
- Is Single: ❌
- Is Tree: ❌

| Label | Type | Options | Notes |
|-------|------|---------|-------|
| Deliverable Name | Data | | |
| Type | Select | Poster\nBanner\nVideo | |
| Assigned To | Link | User | |
| Points | Int | | capacity metric |
| Status | Select | To Do\nIn Progress\nClient Review\nCompleted | |

> When you add the **Table** field, set *Options* = `Deliverable` in Project's Fields grid.

### 5.4 Task
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ❌ (regular DocType)
- Is Child Table: ❌
- Is Single: ❌
- Is Tree: ❌

| Field | Type | Options | Req |
|-------|------|---------|-----|
| Subject | Data | | ✅ |
| Project | Link | Project | ✅ |
| Deliverable | Link | Deliverable | |
| Assigned Designer | Link | User | |
| ETA | Datetime | | |
| Status | Select | Action Pending\nIn Progress\nClient Review\nCompleted | ✅ |
| Paid Rework | Check | | |

> **Kanban:** After saving a few Tasks, go to *Task List ▶ Menu ▶ Kanban Board* ➜ Group by `status` ➜ Save as **Task Board** (shared).

### 5.5 Rework Log
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ❌
- Is Child Table: ❌
- Is Single: ❌
- Is Tree: ❌

Simple transactional DocType linked to Task; similar field layout to Library Transaction example.

### 5.6 QC Review (Submittable)
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ✅
- Is Child Table: ❌
- Is Single: ❌
- Is Tree: ❌

| Field | Type | Options |
|-------|------|---------|
| Task | Link | Task |
| Decision | Select | Approve\nReject |
| Comments | Small Text | |

### 5.7 PM Settings (Singleton)
**DocType Settings (Create dialog):**
- Module: *Project Management*
- Is Submittable: ❌
- Is Child Table: ❌
- Is Single: ✅
- Is Tree: ❌

| Field | Type | Default |
|-------|------|---------|
| Poster Price | Currency | 0 |
| Correction Price | Currency | 0 |
| Default Priority | Select | Medium |

Create with **Is Single** checked. Values are edited once via *Go to PM Settings* button.

Save each DocType → click ⚙ Reload to create boiler-plate python/js.

---
## 6 · ROLES, USERS & PERMISSIONS (Step-by-Step)
1. **Role List** ➜ New ➜ create roles: *Account Manager, Creative Director, Designer, QC Reviewer, Client*.
2. **Role Permissions Manager** ➜ select each DocType ➜ add rows:
   * *Account Manager* – Level 0 – all checkboxes ✔
   * *Creative Director* – read, write, submit on **Task**; read on **Project**; assign on *Deliverable* table.
   * *Designer* – read/write on **Task** where *If Owner* unchecked but *Match fields* = `assigned_designer`.
   * *Client* – Read on Task, Deliverable (via web view) only.
3. **Create sample users**:  
   * Email: `am@example.com` ➜ Add Roles: Account Manager  
   * ... (same for each)
4. Log in as each user to sanity-check permissions.

---
## 7 · WORKFLOWS
### 7.1 Project Workflow
1. **Workflow List** ➜ New
2. State field = `status`; DocType = `Project`.
3. States table:
   | State | Doc Status | Style |
   |-------|-----------|-------|
   | Draft | 0 | Gray |
   | In Progress | 1 | Primary |
   | Client Review | 1 | Warning |
   | Completed | 1 | Success |
   | Rejected | 2 | Danger |
4. Transitions table:
   * Draft → In Progress (Action: *Start Project*, Allowed Role: Account Manager)
   * In Progress → Client Review (*Send to Client*, Account Manager)
   * Client Review → Completed (*Mark Complete*, Client)
   * Client Review → Rejected (*Reject*, Client)
   * Rejected → In Progress (*Revise*, Account Manager)

### 7.2 Task Workflow
Repeat the above; states = Action Pending / In Progress / Client Review / Completed; allowed roles vary.

---
## 8 · UI & UX ENHANCEMENTS
### 8.1 Workspaces / Dashboards
1. *Developer ▶ Workspace* ➜ Duplicate "Home" ➜ Name it **Account Manager**.
2. Remove default shortcuts; add:
   * Number Card: *Total Projects* – DocType Project, Aggregate = count.
   * Chart: Tasks by Status (Group By).
   * Link to Kanban board.
Repeat for Creative Director & Designer.

### 8.2 Custom Form Scripts (JS)
Create `project_management/public/js/task.js`:
```js
frappe.ui.form.on('Task', {
  refresh(frm) {
    if (frm.doc.__islocal) return;
    const canAssign = frappe.user_roles.includes('Account Manager') && frm.doc.status === 'Action Pending';
    if (canAssign) {
      frm.add_custom_button('Assign Designer', () => {
        frappe.prompt([
          {fieldname:'designer', fieldtype:'Link', label:'Designer', options:'User', reqd:1},
          {fieldname:'eta', fieldtype:'Datetime', label:'ETA', reqd:1}
        ], ({designer, eta}) => {
            frm.set_value('assigned_designer', designer);
            frm.set_value('eta', eta);
            frm.save();
        }, 'Assign Task');
      }, 'Actions');
    }
  }
});
```
Run `bench build --app project_management` or just refresh with Ctrl+Shift+R.

---
## 9 · SERVER-SIDE CONTROLLERS (Python)
Path: `project_management/project_management/doctype/project/project.py`
```python
class Project(Document):
    def before_save(self):
        self.deliverable_count = len(self.get("deliverables"))
        self.correction_count = sum(1 for d in self.get("deliverables") if d.get("paid_rework"))
        x = frappe.db.get_single_value("PM Settings", "poster_price") or 0
        y = frappe.db.get_single_value("PM Settings", "correction_price") or 0
        self.grand_total = self.deliverable_count * x + self.correction_count * y
```
Use patterns from `library_transaction.py` for validation logic (duplicate instances blocked, etc.). Remember **bench restart** after changes.

---
## 10 · WEB PORTAL FOR CLIENTS
1. Open **Task DocType** ➜ Web View section ➜ ✔ Has Web View, Route = `client-tasks`.
2. Create templates:
   * `templates/includes/task_row.html` – card for list view.
   * `templates/pages/task.html` – detail page (extends `templates/web.html`).
3. **Portal Settings** (search bar) ➜ Menu ▶ Add Link ➜ `/client-tasks` – visible to role *Client*.
Clients now see only their Tasks with status filter (use Permission Query).

---
## 11 · FILE STORAGE & EXTERNAL
*Native*: each Attach field stores in `File` DocType with `/private/files` path.
*Optional* Drive/R2: implement `project_management/api/storage.py` and hook into `after_insert` of File.

---
## 12 · TESTS & FIXTURES
```bash
bench --site proj.localhost export-fixtures --app project_management --doctype "Workflow,Workspace,Role"
```
Add tests in `test_project.py` using `frappe.get_doc` just like `test_article.py` in tutorial.

---
## 13 · CI / CD
1. `.pre-commit-config.yaml` already set up—run `pre-commit install` once.
2. Add `.github/workflows/ci.yml`:
```yaml
name: Bench Tests
on: [push]
jobs:
  tests:
    runs-on: ubuntu-latest
    services:
      mysql: {image: mariadb:10.6, env: {MYSQL_ROOT_PASSWORD: 123}}    
      redis: {image: redis:6}
    steps:
      - uses: actions/checkout@v4
      - name: Setup Bench
        run: pip install frappe-bench && bench init frappe-bench --skip-assets
      - name: Run tests
        run: bench --site test --app project_management run-tests
```

---
## 14 · DEPLOYMENT (Production)
A. **Easy Single-Server**
```bash
sudo bench setup production frappe
```
* Installs Supervisor + Nginx conf.
* SSL via `bench setup lets-encrypt proj.yourdomain.com`.

B. **Docker Compose** – add `docker-compose.yml` (see official Frappe images) and mount `apps/project_management`.

Hardening checklist: fail2ban, redis persistence, nightly `bench backup`.

---
## 15 · OPERATIONAL WORKFLOW NARRATIVE  🛠️
Below is an end-to-end scenario showing how the system is *actually used* day-to-day.

1. **Account Manager** logs in ⇒  *Account Manager* workspace appears, showing **Total Projects = 0**.
2. Click **New ▶ Project** → fill Project Name, Priority, pick Client (or create inline), choose Due Date.
3. In the Deliverables child-table add rows (Poster, Banner …). Save. Status = *Draft*.
4. Hit **Start Project** (Workflow action) → Status changes to **In Progress**.
5. Project auto-creates Tasks (optional script) or AM goes to **Task Board**; new cards show in *Action Pending*.
6. AM selects a card → presses *Assign Designer* custom button → picks designer & ETA. Task moves to *In Progress*.
7. **Designer** logs in ⇒ sees **Designer Kanban** (To Do column). Opens Task, downloads reference files via Attachments, works on design.
8. Designer uploads design file version 1, sets Task status to **Client Review**, which fires an email to AM/CD.
9. **QC Reviewer** workspace lists Task in *Pending Review*. QC opens Task, creates **QC Review** record, chooses *Approve*.
10. Task status auto-updates to **Client Review** (for Client). Email with secure link sent to client.
11. **Client** clicks web link, logs into Portal, reviews design.  
    a. If satisfied ➜ presses **Approve** → Task status **Completed** → Project progress bar updates.  
    b. If changes needed ➜ presses **Request Revision** → Task status **Action Pending**, Rework Log created (toggle Paid/Free).
12. AM/CD follow up; financial totals in Project recalc: `grand_total = m×poster_price + n×correction_price`.
13. When all Tasks Completed, AM opens Project and clicks **Mark Complete**. Project's DocStatus = Submitted. Grand Total visible for invoicing.
14. **Reports**: CD opens *Designer Capacity* report built with Report Builder, using Deliverable points to gauge workload.

> **Key Takeaway:** Every interaction above maps to a DocType save, a Workflow transition, or a controller hook—mirroring the Library tutorial's patterns.

---
## 16 · PHASE-2 BACKLOG
- 🔍 Deliverable tagging & full-text search for Designers
- 🤖 AI plagiarism scan in QC Review (integrate third-party API)
- ☁️ S3/R2/Google Drive file backend
- 📊 Advanced analytics dashboard (designer utilisation, revenue)

---
### YOU ARE NOW READY 🎉
Update `progress.md` as you finish each milestone and push to Git. Happy building! 