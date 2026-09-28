from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: str = Field(..., min_length=8)

class UserLogin(UserBase):
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)