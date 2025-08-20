from fastapi import APIRouter, Body, Depends, Request, Response, HTTPException, status # type: ignore
from fastapi.encoders import jsonable_encoder # type: ignore
from typing import List
from bson.objectid import ObjectId

import sys
sys.path.append("..")

from helpers import get_password_hash, get_current_user
from models import User, User_In, User_Out

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User_Out)
def create_user(request: Request, user: User_In = Body(...)):
    user = jsonable_encoder(user)
    hash_password = get_password_hash(user['password'])
    user.pop('password')
    user.update([
        ('password_hash', hash_password),
        ('role', 'standard')
    ])
    new_user = request.app.database["users"].insert_one(user)
    created_user = request.app.database["users"].find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user

@router.get("", response_description="List all users", response_model=List[User_Out])
def list_users(request: Request, current_user: User_Out = Depends(get_current_user)):
    if current_user.role == 'admin':
        users = list(request.app.database["users"].find(limit=100))
        return users
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.get("/{id}", response_description="Get a user by id", response_model=User_Out)
def find_user(id: str, request: Request, current_user: User_Out = Depends(get_current_user)):
    if (user := request.app.database["users"].find_one({"_id": ObjectId(id)})) is not None:
        if current_user.role == 'admin' or str(current_user.id) == id:
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")

@router.delete("/{id}", response_description="Delete a user")
def delete_user(id: str, request: Request, response: Response, current_user: User_Out = Depends(get_current_user)):
    if current_user.role == 'admin' or str(current_user.id) == id:
        delete_result = request.app.database["users"].delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            response.status_code = status.HTTP_204_NO_CONTENT
            return response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

# add a patch route for updating user profile (name and email only)
@router.patch("/{id}", response_description="Update user role", response_model=User_Out)
def update_user(id: str, request: Request, user: User = Body(...), current_user: User_Out = Depends(get_current_user)):
    user = jsonable_encoder(user)
    if request.app.database["users"].find_one({"_id": ObjectId(id)}) is not None:
        if current_user.role == 'admin' or str(current_user.id) == id:
            request.app.database["users"].update_one(
                {"_id": ObjectId(id)},
                {"$set": {"first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "email": user["email"]
                        }
                }      
            )
            user_to_return = request.app.database["users"].find_one({"_id": ObjectId(id)})
            return user_to_return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")