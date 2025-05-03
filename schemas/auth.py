from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    role_id: int

class TokenData(BaseModel):
    email: Optional[str] = None
    
class LoginRequest(BaseModel):
    email: str
    password: str
