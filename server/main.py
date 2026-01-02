from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import os
import shutil

from database import engine, get_db, Base
import models
import schemas
import auth
from integrations import search_candidates

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TRACE API", description="Backend for TRACE: AI-Driven Team Formation")

# Mount uploads directory to serve files
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to TRACE API"}

# --- Auth Endpoints ---

@app.post("/auth/signup", response_model=schemas.Token)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create empty profile for user
    new_profile = models.Profile(user_id=new_user.id, full_name="", skills=[])
    db.add(new_profile)
    db.commit()

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Profile Endpoints ---

@app.get("/api/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/api/profile", response_model=schemas.Profile)
async def update_profile(
    profile_update: schemas.ProfileUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        profile = models.Profile(user_id=current_user.id)
        db.add(profile)
    
    for key, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

@app.post("/api/upload")
async def upload_certificate(
    file: UploadFile = File(...),
    description: str = "",
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    file_location = f"uploads/{current_user.id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Generate URL (assuming local serving)
    # In production, this would be an S3 URL
    url = f"http://localhost:8000/{file_location}"
    
    certificate = models.Certificate(
        user_id=current_user.id,
        filename=file.filename,
        description=description,
        url=url
    )
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    return {"info": "file saved", "url": url}

# --- Search Capability (Preserved) ---

MOCK_CANDIDATES = [
    {
        "id": 1,
        "name": "Sarah Chen",
        "role": "Senior React Developer",
        "verified": True,
        "skills": ["React", "TypeScript", "Node.js"],
        "linkedin": "https://www.linkedin.com/search/results/all/?keywords=Sarah+Chen+React",
        "github": "https://github.com/search?q=Sarah+Chen+React",
        "image": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        "experience": "5 years"
    },
    {
        "id": 2,
        "name": "Marcus Johnson",
        "role": "Full Stack Engineer",
        "verified": True,
        "skills": ["Python", "FastAPI", "React"],
        "linkedin": "https://www.linkedin.com/search/results/all/?keywords=Marcus+Johnson+Python",
        "github": "https://github.com/search?q=Marcus+Johnson+Python",
        "image": "https://api.dicebear.com/7.x/avataaars/svg?seed=Marcus",
        "experience": "4 years"
    },
    {
        "id": 3,
        "name": "Emma Wilson",
        "role": "UI/UX Designer",
        "verified": True,
        "skills": ["Figma", "Tailwind CSS", "User Research"],
        "linkedin": "https://www.linkedin.com/search/results/all/?keywords=Emma+Wilson+Designer",
        "github": "https://github.com/search?q=Emma+Wilson+Designer",
        "image": "https://api.dicebear.com/7.x/avataaars/svg?seed=Emma",
        "experience": "3 years"
    },
     {
        "id": 4,
        "name": "Alex Rodriguez",
        "role": "Backend Engineer",
        "verified": False,
        "skills": ["Go", "Docker", "Kubernetes"],
        "linkedin": "https://www.linkedin.com/search/results/all/?keywords=Alex+Rodriguez+Go",
        "github": "https://github.com/search?q=Alex+Rodriguez+Go",
        "image": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
        "experience": "6 years"
    }
]

@app.get("/api/search")
async def search_api(query: str = ""):
    if not query:
        return {"candidates": MOCK_CANDIDATES}
    
    # Use real integration
    results = await search_candidates(query)
    
    # Fallback if no results found or API fails
    if not results:
         query_lower = query.lower()
         terms = query_lower.split()
         results = []
         for c in MOCK_CANDIDATES:
             # Create a searchable string from all candidate fields
             searchable_text = f"{c['name']} {c['role']} {' '.join(c['skills'])}".lower()
             
             # Check if ANY of the search terms exist in the candidate data ("Free" search)
             if any(term in searchable_text for term in terms):
                 results.append(c)
             # Also allow partial matches for the full query string (for cases like "Engineer")
             elif query_lower in searchable_text:
                 results.append(c)


    return {"candidates": results}
