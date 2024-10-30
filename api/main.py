# main.py
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .db import engine, get_db

from passlib.context import CryptContext

app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=engine)



@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if a user with the same email already exists
    existing_email_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Check if a user with the same phone number already exists
    existing_phone_user = db.query(models.User).filter(models.User.phone == user.phone).first()
    if existing_phone_user:
        raise HTTPException(status_code=400, detail="Phone number already exists")
    
    # If no existing user found, proceed to create a new user
    db_user = crud.create_user(db=db, user=user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User could not be created")
    
    return db_user


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/login/", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Retrieve the user by email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Verify the password
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Create JWT token
    access_token = auth.create_access_token(data={"sub": str(db_user.id)})  # Use user ID as subject
    
    return {"access_token": access_token, "token_type": "bearer"}




@app.post("/send-otp/")
def send_otp_endpoint(request: schemas.OTPSendRequest, db: Session = Depends(get_db)):
    # Check if user with the provided phone number exists in the database
    db_user = db.query(models.User).filter(models.User.phone == request.phone_number).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist")

    # If user exists, send the OTP
    auth.send_otp(request.phone_number)
    return {"message": "OTP sent successfully"}

@app.post("/login-with-otp/")
def login_with_otp_endpoint(request: schemas.OTPLoginRequest):
    return auth.login_with_otp(request.phone_number, request.otp)