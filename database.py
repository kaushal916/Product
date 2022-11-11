from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2

import yaml

with open("config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)




DATABASE_URI = "postgresql://" + data['database']['username'] + ":" + data['database']['password'] + "@localhost/"+ data['database']['db']
engine = create_engine(
    DATABASE_URI,    pool_pre_ping=True, 
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
