## Functions and classes for morpc-purpleair-fetch

# Import dependencies
import pandas as pd
import geopandas as gpd

from sqlalchemy import create_engine
from sqlalchemy.event import listen
from geoalchemy2 import load_spatialite
from sqlalchemy.orm import Session

from .model import Sensor, Location, Deployment, Base

# Create engine to store in memory for development

engine = create_engine(
    "sqlite://",
    echo=True)
listen(engine, "connect", load_spatialite) # load spatialite plugin on connect

Base.metadata.create_all(engine)