from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy import Text



Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    embedding = Column(Vector(768))  # size may depend on model
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, index=True)
    user_input = Column(Text)
    retrieved_context = Column(Text)
    model_output = Column(Text)
    latency_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
