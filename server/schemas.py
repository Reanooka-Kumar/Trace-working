from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class CertificateBase(BaseModel):
    description: str

class CertificateCreate(CertificateBase):
    pass

class Certificate(CertificateBase):
    id: int
    user_id: int
    filename: str
    url: str

    class Config:
        orm_mode = True

class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    experience: Optional[str] = None
    skills: List[str] = []
    bio: Optional[str] = None
    image_url: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int
    
    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    email: str
    is_verified: bool
    profile: Optional[Profile] = None
    certificates: List[Certificate] = []

    class Config:
        orm_mode = True
