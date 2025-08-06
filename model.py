from sqlalchemy import Date, DateTime, Float, create_engine, ForeignKey, null
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.event import listen
from geoalchemy2 import Geometry, load_spatialite
from typing import List, Optional
from datetime import datetime, date

# Create engine to store in memory for development
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    plugins=['geoalchemy'],
    echo=True)
listen(engine, "connect", load_spatialite) # load spatialite plugin on connect

# Create base class
class Base(DeclarativeBase):
    pass

class Sensor(Base):
    __tablename__ = "sensor_table"

    # Primary key
    sensor_id: Mapped[int] = mapped_column(primary_key=True)

    # Other columns for sensors
    type: Mapped[str]
    mac_addr: Mapped[str] # Potentially length limit
    notes: Mapped[Optional[str]]
    owner: Mapped[Optional[str]] # Potentially change to enum

    # Define relationships with deployments and locations

    # One to many with deployments. A sensor may be delpoyed multiple times in its lifecycle
    deployments: Mapped[List["Deployment"]] = relationship() 

    def __repr__(self):
        return f"<Sensor ({self.sensor_id})>" # the representation of the class for debuging etc.
    
class Location(Base):
    __tablename__ = "location_table"

    # Primary key
    location_id: Mapped[int] = mapped_column(primary_key=True)

    # Other columns for locations
    name: Mapped[str]
    description: Mapped[Optional[str]]
    LSN: Mapped[Optional[str]]
    zip: Mapped[Optional[str]]
    lat: Mapped[float]
    lon: Mapped[float]

    # Point for location
    geometry = mapped_column(Geometry('POINT')) # Map Point geometry, see https://geoalchemy-2.readthedocs.io/en/stable/orm_tutorial.html#orm-tutorial

    # Many deployments to one location:
    #   Each location may have multiple deployments over time if a sensor changes
    #   A location may also have multiple sensor deployed
    #   This will also need to populate in deployments
    deployments: Mapped[List["Deployment"]] = relationship(back_populates="location")

    def __repr__(self):
        return f"<Location ({self.location_id}, {self.name})>"


class Deployment(Base):
    __tablename__ = "deployment_table"

    # Primary Key
    deploy_id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys for populating sensor and locations
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensor_table.sensor_id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("location_table.location_id"))

    # The beginning and end of the deployment
    start_date: Mapped[date]
    end_date: Mapped[date | None] = mapped_column(nullable=True)

    # Each deployment is essentially the combination of a location, sensor, and time period.
    sensor: Mapped["Sensor"] = relationship(back_populates="location")
    location: Mapped["Location"] = relationship(back_populates="deployments")


    def __repr__(self):
        return f"<Deployment ({self.deploy_id}, {self.location}, {self.start_date} - {self.end_date})>"

# class PM25(Base):
#     __tablename__ = "pm25_table"

#     pm25_id: Mapped[int] = mapped_column(primary_key=True)
#     datetime: Mapped[datetime] = mapped_column(nullable=False)
#     value: Mapped[float] = mapped_column(nullable=False)
#     unit: Mapped[str]

#     sensor_id: Mapped[int] = mapped_column(ForeignKey("othername_table.othertable_id"))
#     othertable: Mapped["Table"] = relationship(back_populates="")





