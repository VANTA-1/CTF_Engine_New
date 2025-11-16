# main.py

# --- STANDARD LIBRARY IMPORTS ---
import os
from typing import List

# --- THIRD-PARTY LIBRARY IMPORTS ---
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

# --- LOCAL APPLICATION IMPORTS ---
import crud, models, schemas
from database import SessionLocal, engine

# --- PYDANTIC MODELS (SCHEMAS FOR REQUEST/RESPONSE) ---
class FlagSubmission(BaseModel):
    """Schema for a flag submission request."""
    flag: str

# --- APPLICATION SETUP ---
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- MIDDLEWARE CONFIGURATION ---
# Allow all origins for development purposes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STATIC FILES CONFIGURATION ---
# Create a 'static' directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- API ENDPOINTS ---
# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Root endpoint to serve the frontend
@app.get("/", response_class=HTMLResponse)
async def read_index():
    # Serve the index.html file from the root directory
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

# Endpoint to get an authentication token
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.username, "token_type": "bearer"}

# Endpoint to read current user info
@app.get("/users/me", response_model=schemas.User)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=token)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Endpoint to read all challenges
@app.get("/challenges/", response_model=List[schemas.Challenge])
def read_challenges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    challenges = crud.get_challenges(db, skip=skip, limit=limit)
    return challenges

# Endpoint to read a single challenge
@app.get("/challenges/{challenge_id}", response_model=schemas.Challenge)
def read_challenge(challenge_id: int, db: Session = Depends(get_db)):
    db_challenge = crud.get_challenge(db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenge

# Endpoint to submit a flag for a challenge
@app.post("/challenges/{challenge_id}/submit")
async def submit_flag(
    challenge_id: int, 
    submission: FlagSubmission,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Accepts a flag submission for a given challenge and returns if it is correct.
    If correct, creates a Solve record for tracking.
    """
    # Get the current user
    user = crud.get_user_by_username(db, username=token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Retrieve the challenge from the database
    db_challenge = crud.get_challenge(db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Compare the submitted flag with the correct flag
    is_correct = submission.flag == db_challenge.flag

    # If correct, check if already solved and create a Solve record if not
    if is_correct:
        existing_solve = db.query(models.Solve).filter(
            models.Solve.user_id == user.id,
            models.Solve.challenge_id == challenge_id
        ).first()
        
        if not existing_solve:
            new_solve = models.Solve(user_id=user.id, challenge_id=challenge_id)
            db.add(new_solve)
            db.commit()
            return {"correct": True, "first_solve": True}
        else:
            return {"correct": True, "first_solve": False}

    return {"correct": False}

# Endpoint for the scoreboard
@app.get("/scoreboard", response_model=List[dict])
def get_scoreboard(db: Session = Depends(get_db)):
    """
    Calculates and returns a ranked list of users based on points from solved challenges.
    """
    # This query joins users, solves, and challenges, then sums the points.
    # It filters out the admin user (ID=1) from the public scoreboard.
    results = db.query(
        models.User.username,
        func.sum(models.Challenge.points).label("total_points")
    ).join(models.Solve, models.User.id == models.Solve.user_id)\
     .join(models.Challenge, models.Solve.challenge_id == models.Challenge.id)\
     .group_by(models.User.username)\
     .order_by(func.sum(models.Challenge.points).desc())\
     .all()

    # Convert the results to a list of dictionaries
    scoreboard = [{"username": row.username, "score": row.total_points} for row in results]
    return scoreboard