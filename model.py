from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional

# Create engine to store in memory for development
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)


class Base(DeclarativeBase):
    pass

class Sensor(Base):
    __tablename__ = "sensor_table"

    sensor_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    mac_addr: Mapped[str]
    notes: Mapped[Optional[str]]
    owner: Mapped[Optional[str]]
    deployments: Mapped[List["Deployment"]] = relationship()

    def __repr__(self):
        return f"<Sensor ({self.sensor_id})>"
    
class Location(Base):
    __tablename__ = "location_table"

    location_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    LSN: Mapped[Optional[str]]
    zip: Mapped[Optional[str]]
    lat: Mapped[float]
    lon: Mapped[float]

class Deployment(Base):
    __tablename__ = "deployment_table"

    deploy_id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensor_table.sensor_id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("location_table.location_id"))
    location: Mapped["Location"] = relationship(back_populates="deployments")


