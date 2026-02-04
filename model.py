from calendar import firstweekday
from re import L
from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, String, Integer, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base, column_property

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

    def __init__(self, id, mac_addr, registration_email, located_outside, deployment_name, public):
        self.id = id
        self.mac_addr = mac_addr
        self.registration_email = registration_email
        self.located_outside = located_outside
        self.deployment_name = deployment_name
        self.public = public

    def __rep__(self):
        return f"registration {self.id}: {self.deployment_name}, mac_addr: {self.mac_addr}"

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

    def __init__(self, id, registration_id, name, index, start_date, end_date, location, hotspot, contact_fullname):
        self.id = id
        self.registration_id = registration_id
        self.name = name
        self.index = index
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.hotspot = hotspot
        self.contact_fullname = contact_fullname

    def __rep__(self):
        return f"deployement {self.id}: {self.name}, {self.start_date}-{self.end_date}, {self.location}"

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    deployments = relationship('Deployment', back_populates='location')
    location_name = Column(String)
    location_desc = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)

    def __init__(self, id, deployments, location_name, location_desc, latitude, longitude, altitude):
        self.id = id
        self.deployments = deployments
        self.location_name = location_name
        self.location_desc = location_desc
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

    def __rep__(self):
        return f"location {self.id}: {self.location_name}, {self.location_desc}"

class Hotspot(Base):
    __tablename__ = 'hotspots'

    id = Column(Integer, primary_key=True)
    deployments = relationship('Deployment', back_populates='hotspot')
    serial = Column(String)
    mac_addr = Column(String)
    ssid = Column(String)
    pwd = Column(String)

    def __init__(self, id, deployments, serial, mac_addr, ssid, pwd):
        self.id = id, 
        self.deployments = deployments
        self.serial = serial
        self.mac_addr = mac_addr
        self.ssid = ssid
        self.pwd = pwd
    
    def __rep__(self):
        return f"hotspot {self.id}: {self.mac_addr}, {self.serial}"

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    deployments = relationship('Deployments', back_populates='contact_fullname')
    firstname = Column(String)
    lastname = Column(String)
    fullname = column_property(firstname + " " + lastname)
    email = Column(String)
    phone = Column(String)

    def __init__(self, id, deployments, firstname, lastname, fullname, email, phone):
        self.id = id
        self.deployments = deployments
        self.firstname = firstname
        self.lastname = lastname
        self.fullname = fullname
        self.email = email
        self.phone = phone
    
    def __rep__(self):
        return f"contact {self.id}: {self.fullname}, {self.email} {self.phone}"


Base.metadata.create_all(bind=engine)