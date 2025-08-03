# Schedula API Server 🗓️

[](https://www.google.com/search?q=https://github.com/codex-mohan/schedula/actions)
[](https://www.python.org/)
[](https://fastapi.tiangolo.com/)
[](https://neon.tech/)
[](https://www.uvicorn.org/)
[](https://render.com/)

A robust and deployable API server for healthcare appointment management, built with FastAPI and backed by a persistent Neon PostgreSQL database. This project leverages modern Python practices and is designed for easy deployment on cloud platforms like Render.

---

## 🚀 Project Information

- **Team Name:** AetherOps
- **Members:** Mohana Krishna (23BAI10630)
- **University:** VIT Bhopal University
- **Hackathon Theme:** "Automation Using Agentic AI – Let Intelligence Take the Lead"

---

## ✨ Features

- **Patient Management:** Register new patients and search for existing ones.
- **Doctor Management:** Add, list, and remove doctor profiles with details like department, experience, and qualifications.
- **Appointment Management:**
  - Book appointments for patients with specific doctors, dates, and times.
  - Reschedule existing appointments.
  - Cancel appointments.
  - Retrieve appointments by patient ID or by doctor ID and date.
- **Persistent Data Storage:** All patient, doctor, and appointment data is stored securely and persistently in a Neon PostgreSQL database.
- **CORS Enabled:** Allows secure cross-origin requests from web clients.
- **Scalable & Deployable:** Designed for easy deployment on cloud platforms (e.g., Render, Railway, Deta).

---

## 🛠️ Technologies Used

- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database:** [Neon PostgreSQL](https://neon.tech/)
- **PostgreSQL Driver:** `psycopg2-binary`
- **Package Manager:** [uv](https://astral.sh/uv)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
- **Environment Variables:** `python-dotenv` (for local development)

---

## 💻 Local Development Setup

Follow these steps to get the Schedula API server running on your local machine.

### Prerequisites

- **Python 3.9+**: Ensure you have a compatible Python version installed.

- **uv**: The `uv` package manager is used for dependency management. If you don't have `uv` installed, you can install it via:

  **macOS and Linux:**

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  **Windows (PowerShell, run as Administrator):**

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 1\. Clone the Repository

First, clone the project repository and navigate to the `neondb` branch:

```bash
git clone https://github.com/codex-mohan/schedula.git
cd schedula
git checkout neondb
```

### 2\. Install Dependencies

Use `uv` to install all project dependencies:

```bash
uv sync
```

### 3\. Set Up Environment Variables

This project uses a Neon PostgreSQL database for persistent storage. You'll need to set the `DATABASE_URL` environment variable.

**a) Get Your Neon DB Connection String:**

1.  Sign up for a free account at [Neon.tech](https://neon.tech/).
2.  Create a new project.
3.  On your project dashboard, locate and copy the **Connection String**. It will look something like:
    `postgresql://[user]:[password]@[host]/[dbname]?sslmode=require`

**b) Create a `.env` file:**
In the root directory of your project (same level as `main.py`), create a file named `.env` and add your Neon database connection string:

```dotenv
# .env
DATABASE_URL="postgresql://[user]:[password]@[host]/[dbname]?sslmode=require"
```

Replace `[user]`, `[password]`, `[host]`, and `[dbname]` with your actual Neon credentials.

### 4\. Database Schema Creation and Migration

Your application's database schema (tables for patients, doctors, appointments, and timings) will be automatically created when the `main.py` application starts up for the first time.

If you had existing doctor data in `doctors.json` from a previous setup and want to migrate it to the Neon DB, follow these steps:

**a) Ensure `doctors.json` is present:**
Make sure the `doctors.json` file (if it contains data you wish to migrate) is in the root directory of your project.

**b) Run the migration script:**
Execute the `migrate_doctors.py` script once. This will read doctors from your local `doctors.json` and insert them into your Neon database.

```bash
python migrate_doctors.py
```

> **Note:** This script will only run if the `doctors` table is empty to prevent duplicate entries.

### 5\. Run the Application

Once dependencies are installed and environment variables are set, start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`. You can view the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

---

## 🧪 API Endpoints (cURL Examples)

Here are `curl` commands to interact with your deployed API at `https://schedula-ouql.onrender.com`. Remember to replace placeholders like `PASTE_YOUR_PATIENT_ID_HERE` with actual IDs from previous responses.

### 1\. Root Endpoint

```bash
curl -X GET "https://schedula-ouql.onrender.com/"
```

### 2\. Patient Endpoints

**a) Register a New Patient**

```bash
curl -X POST "https://schedula-ouql.onrender.com/patients/register" \
-H "Content-Type: application/json" \
-d '{
  "name": "Alice Wonderland",
  "dob": "1992-03-25",
  "contact": "alice.w@example.com"
}'
```

_(Copy `patient_id` from the output)_

**b) Search for a Patient**

```bash
curl -X GET "https://schedula-ouql.onrender.com/patients/search?name=Alice%20Wonderland&dob=1992-03-25"
```

### 3\. Doctor Endpoints

**a) Add a New Doctor**

```bash
curl -X POST "https://schedula-ouql.onrender.com/doctors/add" \
-H "Content-Type: application/json" \
-d '{
  "id": "dr-alice-jones",
  "name": "Dr. Alice Jones",
  "department": "General Practice",
  "experience": 7,
  "success_rate": 91.5,
  "qualification": "MBBS",
  "room": "GP-101"
}'
```

_(Copy `doctor_id` from the output)_

**b) List All Doctors**

```bash
curl -X GET "https://schedula-ouql.onrender.com/doctors"
```

**c) Remove a Doctor**

```bash
curl -X DELETE "https://schedula-ouql.onrender.com/doctors/remove/dr-alice-jones"
```

### 4\. Appointment Endpoints

**a) Book a New Appointment**

```bash
curl -X POST "https://schedula-ouql.onrender.com/appointments/book" \
-H "Content-Type: application/json" \
-d '{
  "patient_id": "PASTE_YOUR_PATIENT_ID_HERE",
  "doctor_id": "dr-alice-jones",
  "date": "2025-09-01",
  "time": "09:00:00",
  "notes": "Routine check-up"
}'
```

_(Copy `appointment_id` from the output)_

**b) Get a Patient's Appointments**

```bash
curl -X GET "https://schedula-ouql.onrender.com/appointments/PASTE_YOUR_PATIENT_ID_HERE"
```

**c) Get a Doctor's Appointments on a Specific Date**

```bash
curl -X GET "https://schedula-ouql.onrender.com/appointments/doctor/dr-alice-jones/2025-09-01"
```

**d) Reschedule an Appointment**

```bash
curl -X PUT "https://schedula-ouql.onrender.com/appointments/reschedule/PASTE_YOUR_APPOINTMENT_ID_HERE?new_date=2025-09-03&new_time=10:00:00"
```

**e) Cancel an Appointment**

```bash
curl -X DELETE "https://schedula-ouql.onrender.com/appointments/cancel/PASTE_YOUR_APPOINTMENT_ID_HERE"
```

---

## ☁️ Deployment on Render

This project is configured for seamless deployment on Render.

1.  **Push to GitHub:** Ensure your code is pushed to your GitHub repository (specifically the `neondb` branch).
2.  **Connect to Render:** Log in to your Render account, click "New Web Service," and connect your GitHub repository.
3.  **Configure Build & Start Commands:**
    - **Build Command:** `uv sync`
    - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  **Set Environment Variable:** Add an environment variable named `DATABASE_URL` with your Neon PostgreSQL connection string as its value.
5.  **Deploy:** Render will automatically build and deploy your application. Subsequent pushes to your `neondb` branch will trigger automatic redeployments.

---

## 🔮 Future Enhancements

- **Authentication and Authorization:** Implement user authentication (e.g., JWT) and role-based access control for patients, doctors, and administrators.
- **Doctor Availability Slots:** Integrate the `doctor_timings` table to manage precise availability slots for doctors, preventing manual time slot conflicts.
- **Notifications:** Add email or SMS notifications for appointment confirmations, reminders, and changes.
- **Search and Filtering:** Enhance search capabilities for appointments and doctors with more advanced filtering options (e.g., by department, status, date range).
- **Frontend Integration:** Develop a user-friendly web or mobile frontend to interact with this API.
- **Admin Panel:** Create a dedicated interface for administrators to manage patients, doctors, and appointments.
- **Testing:** Implement comprehensive unit and integration tests for all API endpoints.
