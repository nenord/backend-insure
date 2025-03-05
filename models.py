import uuid
from pydantic import BaseModel, Field, EmailStr # type: ignore

class User(BaseModel):
    first_name: str = Field(title="User first name: 3-32 characters", min_length=3, max_length=32)
    last_name: str = Field(title="User last name: 3-32 characters", min_length=3, max_length=32)
    email: EmailStr = Field( title="User email")
    id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="_id")

class User_In(User):
    password: str = Field(title="Password to be hashed", min_length=8, max_length=32)

class User_InDB(User):
    password_hash: str = Field(title="Hashed password")
    role: str = Field(title="User role")

class User_Out(User):
    role: str = Field(title="User role")
