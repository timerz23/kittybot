import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


# the secret configuration specific things
from dotenv import load_dotenv
# apparently, no error appears even if the path does not exists
load_dotenv("config.env")
from sample_config import Config


def start() -> scoped_session:
    engine = create_engine(Config.DB_URI)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


try:
    BASE = declarative_base()
    SESSION = start()
except AttributeError as e:
    # this is a dirty way for the work-around required for #23
    print("DB_URI is not configured. Features depending on the database might have issues.")
    print(str(e))

