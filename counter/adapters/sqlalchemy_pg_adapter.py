from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List

Base = declarative_base()


class ObjectCount_PG(Base):
    __tablename__ = "object_counts"

    id = Column(Integer, primary_key=True)
    object_class = Column(String, unique=True)
    count = Column(Integer)


def engine(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session
