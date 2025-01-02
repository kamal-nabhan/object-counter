from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict

Base = declarative_base()


class ObjectCount_PG(Base):
    __tablename__ = "object_counts"

    id = Column(Integer, primary_key=True)
    object_class = Column(String, unique=True)
    count = Column(Integer)

    # Return a dictionary for each object in the database
    def to_dict(self) -> Dict:
        return {"id": self.id, "object_class": self.object_class, "count": self.count}


def engine(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session
