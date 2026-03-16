# THIS FILE IS ONLY ESSENTIAL FOR THE DATABASE CONNECTION ONLY.
# LIKE WHERE IS THE DATABASE LOCATION.
# DOES THAT CONNECTED OR NOT.
# AND HOW THAT WAS CONNECTED.
# AND WHAT KIND OF DATABASE WE ARE USING - 
# sqlite, postgreSQL, MySQL 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import dotenv_values, load_dotenv

import os

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionalMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)



Base = declarative_base()

