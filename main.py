# Schedula API Server
# A deployable API for appointment management using FastAPI + SQLite.
# Deployable on Render, Railway, or Deta with data persistence.
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Date, Time, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os

# Database setup (SQLite for persistence)
# For Render, use persistent disk
if os.environ.get("RENDER"):
    DATABASE_URL = "sqlite:////var/data/schedula.db"
else:
    DATABASE_URL = "sqlite:///./schedula.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# CORS for web crawlers and clients
app = FastAPI(
    title="Schedula API",
    description="API for healthcare appointment management.",
    version="1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB Models
class PatientDB(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    dob = Column(String)
    contact = Column(String)


class AppointmentDB(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    doctor_id = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    notes = Column(String, default="")


Base.metadata.create_all(bind=engine)

# Doctors List (expanded with more departments)
doctors = [
    # Original doctors
    {
        "id": "doc1",
        "name": "Dr. Asha Reddy",
        "department": "Cardiology",
        "experience": 15,
        "success_rate": 98,
        "qualification": "MD Cardiology",
        "room": "Ward 1",
    },
    {
        "id": "doc2",
        "name": "Dr. Rahul Verma",
        "department": "Neurology",
        "experience": 12,
        "success_rate": 96,
        "qualification": "DM Neurology",
        "room": "Ward 2",
    },
    {
        "id": "doc3",
        "name": "Dr. Priya Nair",
        "department": "Orthopedics",
        "experience": 10,
        "success_rate": 94,
        "qualification": "MS Ortho",
        "room": "Ward 3",
    },
    {
        "id": "doc4",
        "name": "Dr. Kavita Joshi",
        "department": "Pediatrics",
        "experience": 8,
        "success_rate": 97,
        "qualification": "MD Pediatrics",
        "room": "Ward 4",
    },
    {
        "id": "doc5",
        "name": "Dr. Anil Kumar",
        "department": "Dermatology",
        "experience": 11,
        "success_rate": 95,
        "qualification": "MD Dermatology",
        "room": "Ward 5",
    },
    {
        "id": "doc6",
        "name": "Dr. Meera Singh",
        "department": "Gynecology",
        "experience": 14,
        "success_rate": 99,
        "qualification": "MD Gynecology",
        "room": "Ward 6",
    },
    {
        "id": "doc7",
        "name": "Dr. Vishal Rao",
        "department": "ENT",
        "experience": 9,
        "success_rate": 93,
        "qualification": "MS ENT",
        "room": "Ward 7",
    },
    {
        "id": "doc8",
        "name": "Dr. Sanjay Gupta",
        "department": "Oncology",
        "experience": 18,
        "success_rate": 85,
        "qualification": "DM Oncology",
        "room": "Ward 8",
    },
    {
        "id": "doc9",
        "name": "Dr. Anjali Sharma",
        "department": "Radiology",
        "experience": 13,
        "success_rate": 97,
        "qualification": "MD Radiology",
        "room": "Radiology Dept 1",
    },
    {
        "id": "doc10",
        "name": "Dr. Rajesh Khanna",
        "department": "Urology",
        "experience": 16,
        "success_rate": 92,
        "qualification": "MS Urology",
        "room": "Ward 9",
    },
    {
        "id": "doc11",
        "name": "Dr. Sunita Patel",
        "department": "Endocrinology",
        "experience": 14,
        "success_rate": 94,
        "qualification": "DM Endocrinology",
        "room": "Ward 10",
    },
    {
        "id": "doc12",
        "name": "Dr. Vikram Malhotra",
        "department": "Gastroenterology",
        "experience": 17,
        "success_rate": 91,
        "qualification": "DM Gastroenterology",
        "room": "Ward 11",
    },
    {
        "id": "doc13",
        "name": "Dr. Neha Agarwal",
        "department": "Pulmonology",
        "experience": 11,
        "success_rate": 93,
        "qualification": "MD Pulmonology",
        "room": "Ward 12",
    },
    {
        "id": "doc14",
        "name": "Dr. Arjun Nair",
        "department": "Nephrology",
        "experience": 15,
        "success_rate": 90,
        "qualification": "DM Nephrology",
        "room": "Ward 13",
    },
    {
        "id": "doc15",
        "name": "Dr. Deepika Menon",
        "department": "Rheumatology",
        "experience": 12,
        "success_rate": 89,
        "qualification": "MD Rheumatology",
        "room": "Ward 14",
    },
    {
        "id": "doc16",
        "name": "Dr. Rohit Verma",
        "department": "Hematology",
        "experience": 10,
        "success_rate": 92,
        "qualification": "MD Hematology",
        "room": "Ward 15",
    },
    {
        "id": "doc17",
        "name": "Dr. Kavita Desai",
        "department": "Psychiatry",
        "experience": 20,
        "success_rate": 88,
        "qualification": "MD Psychiatry",
        "room": "OPD 1",
    },
    {
        "id": "doc18",
        "name": "Dr. Sameer Khan",
        "department": "Ophthalmology",
        "experience": 13,
        "success_rate": 96,
        "qualification": "MS Ophthalmology",
        "room": "Eye Care Unit 1",
    },
    {
        "id": "doc19",
        "name": "Dr. Preeti Singh",
        "department": "Dentistry",
        "experience": 9,
        "success_rate": 98,
        "qualification": "MDS Prosthodontics",
        "room": "Dental Unit 1",
    },
    {
        "id": "doc20",
        "name": "Dr. Amitabh Choudhary",
        "department": "Anesthesiology",
        "experience": 22,
        "success_rate": 99,
        "qualification": "MD Anesthesiology",
        "room": "OT Complex",
    },
]


# Pydantic Models
class Patient(BaseModel):
    id: Optional[str] = None
    name: str
    dob: str  # YYYY-MM-DD
    contact: str


class Appointment(BaseModel):
    id: Optional[str] = None
    patient_id: str
    doctor_id: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    status: str = "scheduled"
    notes: str = ""


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API Routes
@app.get("/patients/search")
def search_patient(name: str, dob: str, db: Session = Depends(get_db)):
    patient = (
        db.query(PatientDB).filter(PatientDB.name == name, PatientDB.dob == dob).first()
    )
    if patient:
        return patient
    raise HTTPException(status_code=404, detail="Patient not found")


@app.post("/patients/register")
def register_patient(patient: Patient, db: Session = Depends(get_db)):
    existing = (
        db.query(PatientDB)
        .filter(PatientDB.name == patient.name, PatientDB.dob == patient.dob)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")

    patient.id = str(uuid.uuid4())
    db_patient = PatientDB(
        id=patient.id, name=patient.name, dob=patient.dob, contact=patient.contact
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return {"message": "Patient registered", "patient_id": patient.id}


@app.get("/doctors")
def list_doctors():
    return doctors


@app.post("/appointments/book")
def book_appointment(appointment: Appointment, db: Session = Depends(get_db)):
    # Check if patient exists
    patient = db.query(PatientDB).filter(PatientDB.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check if doctor exists
    doctor_exists = any(doc["id"] == appointment.doctor_id for doc in doctors)
    if not doctor_exists:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check for conflicting appointments
    conflict = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == appointment.doctor_id,
            AppointmentDB.date == appointment.date,
            AppointmentDB.time == appointment.time,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )

    if conflict:
        raise HTTPException(status_code=400, detail="Time slot already booked")

    appointment.id = str(uuid.uuid4())
    db_appt = AppointmentDB(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        time=appointment.time,
        status=appointment.status,
        notes=appointment.notes,
    )
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return {"message": "Appointment booked", "appointment_id": appointment.id}


@app.put("/appointments/reschedule/{appointment_id}")
def reschedule_appointment(
    appointment_id: str, date: str, time: str, db: Session = Depends(get_db)
):
    appt = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check for conflicting appointments
    conflict = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == appt.doctor_id,
            AppointmentDB.date == date,
            AppointmentDB.time == time,
            AppointmentDB.id != appointment_id,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )

    if conflict:
        raise HTTPException(status_code=400, detail="Time slot already booked")

    appt.date = date
    appt.time = time
    db.commit()
    return {"message": "Appointment rescheduled"}


@app.delete("/appointments/cancel/{appointment_id}")
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appt = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if appt:
        appt.status = "cancelled"
        db.commit()
        return {"message": "Appointment cancelled"}
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.get("/appointments/{patient_id}")
def get_appointments(patient_id: str, db: Session = Depends(get_db)):
    appts = db.query(AppointmentDB).filter(AppointmentDB.patient_id == patient_id).all()
    return appts


@app.get("/appointments/doctor/{doctor_id}/{date}")
def get_doctor_appointments(doctor_id: str, date: str, db: Session = Depends(get_db)):
    appts = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.date == date,
            AppointmentDB.status != "cancelled",
        )
        .all()
    )
    return appts


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Schedula API - Healthcare Appointment Management System"
    }


# Run Locally:
# uvicorn schedula_api_server:app --reload
