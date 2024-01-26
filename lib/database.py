from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///db.db")
SessionLocal = sessionmaker(bind=engine)