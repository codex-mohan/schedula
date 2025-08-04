import os
import json
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    JSON,
)  # Import JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# --- Configuration (must match your main application) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- DB Model (must match your main application) ---
class DoctorDB(Base):
    __tablename__ = "doctors"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    department = Column(String)
    experience = Column(Integer)
    success_rate = Column(Float)
    qualification = Column(String)
    room = Column(String)
    timings = Column(JSON, default=[])  # Column to store JSON array of timings


# IMPORTANT: Base.metadata.create_all(bind=engine) is REMOVED from here.
# It should only be in your main.py for initial table creation, or handled by a proper migration tool.


# --- Migration Script Logic ---
def migrate_doctors():
    db = SessionLocal()
    try:
        # Check if the doctors table is already populated
        # This check will now work because the 'timings' column exists
        if db.query(DoctorDB).count() > 0:
            print("Doctors table is not empty. Aborting migration.")
            return

        # Load data from the local JSON file
        try:
            with open("doctors.json", "r") as f:
                doctors_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("doctors.json not found or is empty. No data to migrate.")
            return

        print(f"Found {len(doctors_data)} doctors to migrate.")

        # Insert each doctor into the database
        for doctor_dict in doctors_data:
            # SQLAlchemy's JSON type will handle the list of dicts directly
            db_doctor = DoctorDB(**doctor_dict)
            db.add(db_doctor)

        db.commit()
        print("Migration successful! Doctors have been added to the Neon DB.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during migration: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_doctors()
