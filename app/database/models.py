from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database.database import Base
from datetime import datetime

class Quiz(Base):
    __tablename__ = "quizes"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(50), index=True)  # short, searchable
    quiz = Column(Text)  # long quiz content
    created_at = Column(DateTime, default=datetime.now())

class Summary(Base):
    __tablename__ = "summary"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(50), index=True)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    
    
class Topics(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    output_json = Column(Text)
    created_at = Column(DateTime)