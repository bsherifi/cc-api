from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Plan(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    rate_limit = Column(Integer, default=10)  # Requests per minute
    initial_credits = Column(Integer, default=100)

    # Relationship
    users = relationship("User", back_populates="plan")


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(String, unique=True, index=True)
    credits = Column(Integer, default=0)
    
    plan_id = Column(Integer, ForeignKey("plan.id"))
    plan = relationship("Plan", back_populates="users")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    requests = relationship("RequestLog", back_populates="user")


class RequestLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    endpoint = Column(String)
    request_data = Column(String)
    response_data = Column(String)
    status_code = Column(Integer)
    credits_deducted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="requests") 