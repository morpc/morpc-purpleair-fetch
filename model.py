from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, String, Integer, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

DB_URL = 'sqlite:///./test.db'

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Registration(Base):
    __tablename__ = 'registrations'

    # Map columns
    id = Column(Integer, primary_key=True)
    mac_addr = Column(String)
    registration_email = Column(String)
    located_outside = Column(Boolean)
    deployment_name = relationship('Deployment', uselist=False, back_populates='name')
    public = Column(Boolean)


class Deployment(Base):
    __tablename__ = 'deployments'

    id = Column(Integer, primary_key=True)

    # Populate id from registration table
    registration_id = Column(Integer, ForeignKey('registrations.id')) 

    # Population name used as deployment name from registration, 
    # "Location Name" when registering on Purple Air
    name = relationship('Registration', back_populates='deployment_name') 
    index = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    # Deployments of a many to one relationships with locations, hotspots, contacts
    location_id = Column(Integer, ForeignKey('locations.id'))
    location = relationship('Location', back_populates='deployments')

    hotspot_id = Column(Integer, ForeignKey('hotspots.id'))
    hotspot = relationship('Hotspot', back_populates='deployments')


    contact_id = Column(Integer, ForeignKey('contacts.id'))
    contact_fullname = relationship('Contacts', back_populates='deployments')

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    deployments = relationship('Deployment', back_populates='location')
    location_name = Column(String)
    location_desc = Column(String)
    latitude = Column(Float)
    Longitude = Column(Float)
    Altitude = Column(Float)

class Hotspot(Base):
    __tablename__ = 'hotspots'

    id = Column(Integer, primary_key=True)
    deployments = relationship('Deployment', back_populates='hotspot')
    serial = Column(String)
    mac_addr = Column(String)
    ssid = Column(String)
    pwd = Column(String)

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    deployments = relationship('Deployments', back_populates='contact_fullname')
    fullname = Column(String)
    email = Column(String)
    phone = Column(String)


Base.metadata.create_all(bind=engine)







    





