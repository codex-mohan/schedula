import os
import json
import uuid
from datetime import date, time, datetime
from typing import List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Date, Time
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware


# --- JSON-BASED DOCTOR RECORDS ---
DOCTORS_FILE = "doctors.json"


def load_doctors_from_json():
    try:
        with open(DOCTORS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_doctors_to_json(doctors_list: List):
    with open(DOCTORS_FILE, "w") as f:
        json.dump(doctors_list, f, indent=2)


doctors = load_doctors_from_json()

# --- DATABASE SETUP (POSTGRESQL) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- FASTAPI SETUP ---
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


# --- DB MODELS ---
class PatientDB(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    dob = Column(Date)
    contact = Column(String)


class AppointmentDB(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    doctor_id = Column(String, index=True)
    date = Column(Date)
    time = Column(Time)
    status = Column(String, default="scheduled")
    notes = Column(String, default="")


Base.metadata.create_all(bind=engine)


# --- PYDANTIC MODELS ---
class Patient(BaseModel):
    id: Optional[str] = None
    name: str
    dob: date
    contact: str


class Doctor(BaseModel):
    id: str
    name: str
    department: str
    experience: int
    success_rate: float
    qualification: str
    room: str


class Appointment(BaseModel):
    id: Optional[str] = None
    patient_id: str
    doctor_id: str
    date: date
    time: time
    status: str = "scheduled"
    notes: str = ""


# --- DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API ROUTES ---
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Schedula API - Healthcare Appointment Management System"
    }


@app.get("/patients/search")
def search_patient(name: str, dob: date, db: Session = Depends(get_db)):
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


@app.post("/doctors/add")
def add_doctor(doctor: Doctor):
    if any(d["id"] == doctor.id for d in doctors):
        raise HTTPException(
            status_code=400, detail=f"Doctor with ID '{doctor.id}' already exists."
        )

    doctors.append(doctor.model_dump())
    save_doctors_to_json(doctors)
    return {"message": "Doctor added successfully", "doctor_id": doctor.id}


@app.delete("/doctors/remove/{doctor_id}")
def remove_doctor(doctor_id: str):
    global doctors
    doctor_found = any(d["id"] == doctor_id for d in doctors)
    if not doctor_found:
        raise HTTPException(
            status_code=404, detail=f"Doctor with ID '{doctor_id}' not found."
        )

    doctors = [d for d in doctors if d["id"] != doctor_id]
    save_doctors_to_json(doctors)
    return {"message": f"Doctor with ID '{doctor_id}' removed successfully."}


@app.post("/appointments/book")
def book_appointment(appointment: Appointment, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor_exists = any(doc["id"] == appointment.doctor_id for doc in doctors)
    if not doctor_exists:
        raise HTTPException(status_code=404, detail="Doctor not found")

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
    appointment_id: str, new_date: date, new_time: time, db: Session = Depends(get_db)
):
    appt = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    conflict = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == appt.doctor_id,
            AppointmentDB.date == new_date,
            AppointmentDB.time == new_time,
            AppointmentDB.id != appointment_id,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )

    if conflict:
        raise HTTPException(status_code=400, detail="Time slot already booked")

    appt.date = new_date
    appt.time = new_time
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


@app.get("/appointments/doctor/{doctor_id}/{query_date}")
def get_doctor_appointments(
    doctor_id: str, query_date: date, db: Session = Depends(get_db)
):
    appts = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.date == query_date,
            AppointmentDB.status != "cancelled",
        )
        .all()
    )
    return appts


# Run Locally:
# You must first set your DATABASE_URL environment variable.
# For example:
# export DATABASE_URL="postgresql://user:password@host:port/dbname"
#
# Then run the Uvicorn server:
# uvicorn your_file_name:app --reload
