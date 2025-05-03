from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import User
from db.database import get_db
from utils.security import verify_password, create_access_token, get_password_hash
from schemas.auth import Token, LoginRequest
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/create-user/{name}/{email}/{password}/{role_id}", status_code=status.HTTP_201_CREATED)
async def create_user(name: str, email: str, password: str, role_id: int, db: Session = Depends(get_db)):
    # Hash the password before storing
    hashed_password = get_password_hash(password)
    
    # add user to database with hashed password
    user = User(name=name, email=email, password=hashed_password, role_id=role_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/get-user/{name}", status_code=status.HTTP_200_OK)
async def get_user(name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if password matches - temporary handling for both hashed and unhashed passwords
    password_matches = False
    try:
        # Try to verify against a hashed password
        password_matches = verify_password(form_data.password, user.password)
    except:
        # If verification fails, check direct equality (for legacy passwords)
        password_matches = form_data.password == user.password
    
    if not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        role_id=user.role_id
    )
