from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    workshop_id = Column(Integer, ForeignKey('workshops.id'), nullable=False)
    registered_at = Column(DateTime, default=func.now())

    student = relationship("Student", back_populates="registrations")
    workshop = relationship("Workshop", back_populates="registrations")

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    student_code = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    registrations = relationship("Registration", back_populates="student")
    workshops = relationship("Workshop", secondary="registrations", back_populates="students")

class Workshop(Base):
    __tablename__ = 'workshops'

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    maximum_participants = Column(Integer, nullable=False)

    registrations = relationship("Registration", back_populates="workshop")
    students = relationship("Student", secondary="registrations", back_populates="workshops")