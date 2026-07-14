from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

patient_medication = Table(
    'patient_medication',
    Base.metadata,
    Column('patient_id', Integer, ForeignKey('patients.id'), primary_key=True),
    Column('medication_id', Integer, ForeignKey('medications.id'), primary_key=True)
)

class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=False)

    patients = relationship("Patient", back_populates="doctor")


class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    patient_code = Column(String(100), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))

    doctor = relationship("Doctor", back_populates="patients")
    insurance = relationship("Insurance", back_populates="patient", uselist=False)
    medications = relationship("Medication", secondary=patient_medication, back_populates="patients")


class Insurance(Base):
    __tablename__ = 'insurances'

    id = Column(Integer, primary_key=True)
    insurance_number = Column(String(100), nullable=False)
    expiry_date = Column(Date, nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)

    patient = relationship("Patient", back_populates="insurance")


class Medication(Base):
    __tablename__ = 'medications'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    patients = relationship("Patient", secondary=patient_medication, back_populates="medications")