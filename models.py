# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    solves = relationship("Solve", back_populates="user")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    flag = Column(String)
    points = Column(Integer)
    
    solves = relationship("Solve", back_populates="challenge")

class Solve(Base):
    __tablename__ = "solves"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    solved_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="solves")
    challenge = relationship("Challenge", back_populates="solves")
