from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
    date_joined: str
    is_active: bool

    class Config:
        orm_mode = True