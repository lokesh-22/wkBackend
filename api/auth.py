import os
import random
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from twilio.rest import Client
from fastapi import FastAPI, HTTPException


load_dotenv()

# Twilio credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")



client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# JWT Configuration
SECRET_KEY = "your_secret_key"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OTP storage (in-memory for simplicity, consider a persistent store)
otp_storage = {}

def send_otp(phone_number: str):
    otp = f"{random.randint(100000, 999999)}"  # Generate a 6-digit OTP
    otp_storage[phone_number] = {"otp": otp, "expiry": datetime.now() + timedelta(minutes=5)}

    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number,
    )

    return message.sid  # Optionally return message SID for tracking

def verify_otp(phone_number: str, otp: str):
    if phone_number in otp_storage:
        stored_otp = otp_storage[phone_number]
        if datetime.now() > stored_otp["expiry"]:
            raise HTTPException(status_code=400, detail="OTP expired")
        if stored_otp["otp"] == otp:
            del otp_storage[phone_number]  # Remove OTP after verification
            return True
        else:
            raise HTTPException(status_code=400, detail="Invalid OTP")
    else:
        raise HTTPException(status_code=400, detail="OTP not requested")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# New function for logging in with OTP
def login_with_otp(phone_number: str, otp: str):
    # Verify the OTP
    if verify_otp(phone_number, otp):
        # Create JWT token
        token_data = {"phone_number": phone_number}  # or any other user info
        access_token = create_access_token(data=token_data)
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=400, detail="OTP verification failed")


