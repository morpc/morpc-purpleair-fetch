## Functions and classes for morpc-purpleair-fetch

# Import dependencies
import morpc
import pandas as pd
import geopandas as gpd

from sqlalchemy import create_engine
from sqlalchemy.event import listen
from geoalchemy2 import load_spatialite
from sqlalchemy.orm import Session

from .model import engine, Sensor, Location, Deployment

# Create engine to store in memory for development
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    plugins=['geoalchemy2'],
    echo=True)
listen(engine, "connect", load_spatialite) # load spatialite plugin on connect

with Session(engine) as session:
    engine.metadata()