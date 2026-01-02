from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    
    profile = relationship("Profile", back_populates="user", uselist=False)
    certificates = relationship("Certificate", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String, index=True)
    role = Column(String)
    experience = Column(String)
    skills = Column(JSON, default=[])  # Storing list of strings as JSON
    bio = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    description = Column(String)
    url = Column(String) # URL to access the file

    user = relationship("User", back_populates="certificates")
