# crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from . import models, schemas

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: schemas.UserCreate):
    # Hash the user's password
    hashed_password = pwd_context.hash(user.password)
    
    # Create a new User instance
    db_user = models.User(
        firstname=user.firstname,
        lastname=user.lastname,
        phone=user.phone,
        email=user.email,
        password=hashed_password  # Store hashed password
    )

    # Add the user to the session
    db.add(db_user)
    
    try:
        db.commit()         # Commit only if there’s no error
        db.refresh(db_user)  # Refresh to get the assigned ID
        return db_user
    except SQLAlchemyError as e:
        db.rollback()       # Rollback if there’s an error, no ID is consumed
        print(f"Error creating user: {e}")
        return None

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
