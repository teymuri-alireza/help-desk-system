# Help Desk System

A Help Desk system designed for managing Information Technology (IT) support requests within a university environment.

In addition to core ticket management functions such as tracking, assignment, and communication, the system integrates AI-assisted features including request classification, priority prediction, and intelligent support recommendations

## How to Run

### 1. Create a Python Virtual Environment

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (Command Prompt)
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
uvicorn src.server.app:app
```

The application will start using the `app` instance defined in `src/server/app.py`.

### 4. Open the Application

Open your web browser and navigate to:

```
http://127.0.0.1:8000
```

## Testing

Use the login page to test role-based access with the following users:

- `405100`: admin
- `405101`: IT manager
- `405300`: IT expert
- `405500`: student

Each role has its own access and controls.

## Project Objectives

- Centralized ticket registration and tracking
- Ticket assignment to responsible departments and IT experts
- Support request management and communication
- Notification and status tracking
- Reporting and monitoring of support activities

## Project Scope

The project includes:

- Requirements Analysis
- Use Case Modeling
- Domain Modeling
- Entity-Relationship Design (ERD)
- Database Design
- System Architecture Design
- Role and Permission Design
- REST API Development
- Backend Implementation
- Frontend Implementation

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

### Frontend

- HTML, CSS static pages.

## Repository Structure

```text
diagrams/
├── as-is/
├── domain-model/
├── erd/
├── system-design/
└── use-case/

docs/
├── 01-project-definition/
├── 02-analysis/
└── 03-design/

src/
├── core/
├── database/
└── server/
```
