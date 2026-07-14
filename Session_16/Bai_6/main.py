from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Fleet(Base):
    __tablename__ = 'fleets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    drivers = relationship("Driver", back_populates="fleet")

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    car_id = Column(Integer, ForeignKey('cars.id'))

class Driver(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    status = Column(String(20))
    fleet_id = Column(Integer, ForeignKey('fleets.id'))

    fleet = relationship("Fleet", back_populates="drivers")
    cars = relationship("Car", secondary="bookings", back_populates="drivers")

class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    license_plate = Column(String(20), nullable=False)
    status = Column(String(20))

    drivers = relationship("Driver", secondary="bookings", back_populates="cars")