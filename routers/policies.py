from fastapi import APIRouter, status, Body, Request, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime

from models import Policy, Policy_Out, User_Out, Add_Milage
from helpers import get_current_user, check_vehicle_make, get_policies_by_user_id

import sys
sys.path.append("..")


router = APIRouter(
    prefix="/policies",
    tags=["policies"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_description="Create a new policy", status_code=status.HTTP_201_CREATED, response_model=Policy_Out)
def create_policy(request: Request, policy: Policy = Body(...), current_user: User_Out = Depends(get_current_user)):
    policy = jsonable_encoder(policy)
    #check if policy id is the same as current user id
    if policy["user_id"] != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    #check if vehicle make is in the database
    vehicle_to_check = check_vehicle_make(policy["make"])
    if vehicle_to_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehicle make not found")
    #check if vehicle model is in the database
    if policy["model"] not in vehicle_to_check["models"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehicle model not found")
    policy["mileage_used"] = { datetime.now().isoformat(): 0 }
    new_policy = request.app.database["policies"].insert_one(policy)
    created_user = request.app.database["policies"].find_one(
        {"_id": new_policy.inserted_id}
    )
    return created_user

# add a patch ruote for updating policy milage used field
@router.patch("/{id}", response_description="Update policy mileage used", response_model=Policy_Out)
def update_policy_mileage(id: str, request: Request, mileage: Add_Milage = Body(...), current_user: User_Out = Depends(get_current_user)):
    mileage = jsonable_encoder(mileage)
    policy = request.app.database["policies"].find_one({"_id": ObjectId(id)})
    if policy is not None:
        if policy["user_id"] != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        # find the highest value in policy dictionary
        highest_mileage = max(policy["mileage_used"].values())
        # check if the mileage to be added is greater than the previous highest mileage
        if mileage["mileage"] <= highest_mileage:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mileage must be greater than previous mileage")
        
        policy_milage_to_update = policy["mileage_used"]
        policy_milage_to_update[datetime.now().isoformat()] = mileage["mileage"]
        request.app.database["policies"].update_one(
            {"_id": ObjectId(id)},
            {"$set": {"mileage_used": policy_milage_to_update }}
        )
        updated_policy = request.app.database["policies"].find_one({"_id": ObjectId(id)})
        return updated_policy
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy with ID {id} not found")

@router.get("/", response_description="List all policies", response_model=list[Policy_Out])
def list_policies(request: Request, current_user: User_Out = Depends(get_current_user)):
    if current_user.role != 'admin':
        policies = get_policies_by_user_id(str(current_user.id))
        if not policies:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No policies found")
        return policies
    # if user is admin, return all policies
    policies = list(request.app.database["policies"].find(limit=100))
    return policies

@router.get("/{id}", response_description="Get a policy by id", response_model=Policy_Out)
def find_policy(id: str, request: Request, current_user: User_Out = Depends(get_current_user)):
    if (policy := request.app.database["policies"].find_one({"_id": ObjectId(id)})) is not None:
        if current_user.role == 'admin' or policy["user_id"] == str(current_user.id):
            return policy
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy with ID {id} not found")

@router.delete("/{id}", response_description="Delete a policy")
def delete_policy(id: str, request: Request, response: Response, current_user: User_Out = Depends(get_current_user)):
    if current_user.role == 'admin':
        delete_result = request.app.database["policies"].delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            response.status_code = status.HTTP_204_NO_CONTENT
            return response
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy with ID {id} not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")