import os
import uuid
import logging
from datetime import date, time
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Date, Time, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler

# --- LOGGING SETUP (RICH) ---
# Configure logging to use RichHandler for beautiful, clear logs.
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

# Get a logger instance
log = logging.getLogger("rich")


# --- DATABASE SETUP (POSTGRESQL) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    log.error("[bold red]FATAL: DATABASE_URL environment variable not set.[/bold red]")
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


class DoctorDB(Base):
    __tablename__ = "doctors"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    department = Column(String)
    experience = Column(Integer)
    success_rate = Column(Float)
    qualification = Column(String)
    room = Column(String)
    timings = Column(JSON, default=[])


class AppointmentDB(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    doctor_id = Column(String, index=True)
    date = Column(Date)
    time = Column(Time)
    ward = Column(String)
    status = Column(String, default="scheduled")
    notes = Column(String, default="")


Base.metadata.create_all(bind=engine)


# --- PYDANTIC MODELS ---
class Patient(BaseModel):
    id: Optional[str] = None
    name: str
    dob: date
    contact: str


class TimingSlot(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time


class Doctor(BaseModel):
    id: str
    name: str
    department: str
    experience: int
    success_rate: float
    qualification: str
    room: str
    timings: List[TimingSlot] = []


class Appointment(BaseModel):
    id: Optional[str] = None
    patient_name: str
    patient_dob: date
    patient_contact: Optional[str]
    doctor_name: str
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
    log.info("Root endpoint was hit.")
    return {
        "message": "Welcome to Schedula API - Healthcare Appointment Management System"
    }


@app.get("/patients/search")
def search_patient(name: str, dob: date, db: Session = Depends(get_db)):
    log.info(f"Searching for patient with payload: name='{name}', dob='{dob}'")
    patient = (
        db.query(PatientDB).filter(PatientDB.name == name, PatientDB.dob == dob).first()
    )
    if patient:
        log.info(f"Patient '{name}' found.")
        return patient

    log.warning(f"Patient '{name}' not found.")
    raise HTTPException(status_code=404, detail="Patient not found")


@app.post("/patients/register")
def register_patient(patient: Patient, db: Session = Depends(get_db)):
    log.info(f"Received payload to register patient: {patient.model_dump()}")
    existing = (
        db.query(PatientDB)
        .filter(PatientDB.name == patient.name, PatientDB.dob == patient.dob)
        .first()
    )
    if existing:
        log.error(
            f"Conflict: Patient '{patient.name}' with DOB '{patient.dob}' already exists."
        )
        raise HTTPException(status_code=400, detail="Patient already exists")

    patient.id = str(uuid.uuid4())
    db_patient = PatientDB(
        id=patient.id, name=patient.name, dob=patient.dob, contact=patient.contact
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    log.info(f"Successfully registered patient with ID: {patient.id}")
    return {"message": "Patient registered", "patient_id": patient.id}


@app.get("/doctors")
def list_doctors(db: Session = Depends(get_db)):
    log.info("Request received to list all doctors.")
    doctors = db.query(DoctorDB).all()
    log.info(f"Found {len(doctors)} doctors.")
    return doctors


@app.post("/doctors/add")
def add_doctor(doctor: Doctor, db: Session = Depends(get_db)):
    log.info(f"Received payload to add doctor: {doctor.model_dump()}")
    existing = db.query(DoctorDB).filter(DoctorDB.id == doctor.id).first()
    if existing:
        log.error(f"Conflict: Doctor with ID '{doctor.id}' already exists.")
        raise HTTPException(
            status_code=400, detail=f"Doctor with ID '{doctor.id}' already exists."
        )

    db_doctor = DoctorDB(**doctor.model_dump())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    log.info(f"Successfully added doctor with ID: {doctor.id}")
    return {"message": "Doctor added successfully", "doctor_id": doctor.id}


@app.delete("/doctors/remove/{doctor_id}")
def remove_doctor(doctor_id: str, db: Session = Depends(get_db)):
    log.info(f"Request received to remove doctor with ID: '{doctor_id}'")
    doctor_to_remove = db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
    if not doctor_to_remove:
        log.error(f"Not found: Doctor with ID '{doctor_id}' not found for removal.")
        raise HTTPException(
            status_code=404, detail=f"Doctor with ID '{doctor_id}' not found."
        )

    db.delete(doctor_to_remove)
    db.commit()
    log.info(f"Successfully removed doctor with ID: '{doctor_id}'")
    return {"message": f"Doctor with ID '{doctor_id}' removed successfully."}


@app.post("/appointments/book")
def book_appointment(appointment_data: Appointment, db: Session = Depends(get_db)):
    log.info(f"Received payload to book appointment: {appointment_data.model_dump()}")
    # Find patient by name and DOB
    patient = (
        db.query(PatientDB)
        .filter(
            PatientDB.name == appointment_data.patient_name,
            PatientDB.dob == appointment_data.patient_dob,
        )
        .first()
    )
    if not patient:
        log.error(
            f"Patient not found for booking: name='{appointment_data.patient_name}', dob='{appointment_data.patient_dob}'"
        )
        raise HTTPException(
            status_code=404, detail="Patient not found with provided name and DOB."
        )

    # Find doctor by name
    doctor = (
        db.query(DoctorDB).filter(DoctorDB.name == appointment_data.doctor_name).first()
    )
    if not doctor:
        log.error(
            f"Doctor not found for booking: name='{appointment_data.doctor_name}'"
        )
        raise HTTPException(
            status_code=404, detail="Doctor not found with provided name."
        )

    # Check for conflicting appointments
    conflict = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == doctor.id,
            AppointmentDB.date == appointment_data.date,
            AppointmentDB.time == appointment_data.time,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )

    if conflict:
        log.warning(
            f"Booking conflict detected for doctor '{doctor.name}' at {appointment_data.date} {appointment_data.time}"
        )
        raise HTTPException(status_code=400, detail="Time slot already booked")

    new_appointment_id = str(uuid.uuid4())
    db_appt = AppointmentDB(
        id=new_appointment_id,
        patient_id=patient.id,
        doctor_id=doctor.id,
        date=appointment_data.date,
        time=appointment_data.time,
        status=appointment_data.status,
        notes=appointment_data.notes,
    )
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    log.info(
        f"Successfully booked appointment '{new_appointment_id}' for patient '{patient.name}' with doctor '{doctor.name}'."
    )
    return {"message": "Appointment booked", "appointment_id": new_appointment_id}


@app.put("/appointments/reschedule/{appointment_id}")
def reschedule_appointment(
    appointment_id: str, new_date: date, new_time: time, db: Session = Depends(get_db)
):
    log.info(
        f"Received payload to reschedule appointment_id='{appointment_id}' to date='{new_date}' time='{new_time}'"
    )
    appt = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not appt:
        log.error(f"Appointment with ID '{appointment_id}' not found for rescheduling.")
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
        log.warning(
            f"Reschedule conflict detected for appointment ID '{appointment_id}' at {new_date} {new_time}"
        )
        raise HTTPException(status_code=400, detail="Time slot already booked")

    appt.date = new_date
    appt.time = new_time
    db.commit()
    log.info(f"Successfully rescheduled appointment ID: '{appointment_id}'.")
    return {"message": "Appointment rescheduled"}


@app.delete("/appointments/cancel/{appointment_id}")
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    log.info(f"Request received to cancel appointment with ID: '{appointment_id}'")
    appt = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if appt:
        appt.status = "cancelled"
        db.commit()
        log.info(f"Successfully cancelled appointment ID: '{appointment_id}'.")
        return {"message": "Appointment cancelled"}

    log.error(f"Appointment with ID '{appointment_id}' not found for cancellation.")
    raise HTTPException(status_code=404, detail="Appointment not found")


@app.get("/appointments")
def get_appointments(
    patient_name: str = Query(..., description="Name of the patient"),
    patient_dob: date = Query(
        ..., description="Date of birth of the patient (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
):
    log.info(
        f"Request to get appointments for patient: name='{patient_name}', dob='{patient_dob}'"
    )
    patient = (
        db.query(PatientDB)
        .filter(PatientDB.name == patient_name, PatientDB.dob == patient_dob)
        .first()
    )
    if not patient:
        log.error(
            f"Patient not found when getting appointments: name='{patient_name}', dob='{patient_dob}'"
        )
        raise HTTPException(
            status_code=404, detail="Patient not found with provided name and DOB."
        )

    appts = db.query(AppointmentDB).filter(AppointmentDB.patient_id == patient.id).all()
    log.info(f"Found {len(appts)} appointments for patient '{patient_name}'.")
    return appts


@app.get("/appointments/doctor")
def get_doctor_appointments(
    doctor_name: str = Query(..., description="Name of the doctor"),
    query_date: date = Query(
        ..., description="Date for which to retrieve appointments (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
):
    log.info(
        f"Request to get appointments for doctor: name='{doctor_name}', date='{query_date}'"
    )
    doctor = db.query(DoctorDB).filter(DoctorDB.name == doctor_name).first()
    if not doctor:
        log.error(f"Doctor not found when getting appointments: name='{doctor_name}'")
        raise HTTPException(
            status_code=404, detail="Doctor not found with provided name."
        )

    appts = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == doctor.id,
            AppointmentDB.date == query_date,
            AppointmentDB.status != "cancelled",
        )
        .all()
    )
    log.info(
        f"Found {len(appts)} appointments for doctor '{doctor_name}' on {query_date}."
    )
    return appts
