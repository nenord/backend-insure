from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, BeforeValidator # type: ignore

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    first_name: str = Field(title="User first name: 3-32 characters", min_length=3, max_length=32)
    last_name: str = Field(title="User last name: 3-32 characters", min_length=3, max_length=32)
    email: EmailStr = Field( title="User email")

class User_In(User):
    password: str = Field(title="Password to be hashed", min_length=8, max_length=32)

class User_Out(User):
    role: str = Field(title="User role")
    id: PyObjectId = Field(alias="_id", default=None)

class User_InDB(User_Out):
    password_hash: str = Field(title="Hashed password")

# add a class calld Vehicle that inherits from BaseModel with field called make and model 
# where model is a list of strings
class Vehicle(BaseModel):
    make: str = Field(title="Vehicle make", min_length=1, max_length=32)
    models: list[str] = Field(title="List of vehicle models")

class Vehicle_Out(Vehicle):
    id: PyObjectId = Field(alias="_id", default=None)