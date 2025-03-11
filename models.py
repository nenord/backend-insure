import uuid
from typing import Optional
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
    # add a field called milage inputs that is a list of dictionary objects
    # with the following fields: date, milage
    milage_inputs: list[dict] = Field(title="List of milage inputs")


class User_Out(User):
    role: str = Field(title="User role")

# add a class calld Vehicle that inherits from BaseModel with field called make and model 
# where model is a list of strings
class Vehicle(BaseModel):
    make: str = Field(title="Vehicle make", min_length=1, max_length=32)
    models: list[str] = Field(title="List of vehicle models")