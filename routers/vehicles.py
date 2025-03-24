# This file contains the routes for the vehicles endpoint
from fastapi import APIRouter, Body, Request, HTTPException, status, Depends, Response
from fastapi.encoders import jsonable_encoder   
from typing import List

from models import Vehicle, User_Out, Vehicle_Out
from helpers import check_vehicle_make, get_current_user, combine_lists
from bson.objectid import ObjectId

import sys
sys.path.append("..")

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    responses={404: {"description": "Not found"}}
)

# Add a post route that will create a vehicle in the database
@router.post("/", response_description="Create a new vehicle", status_code=status.HTTP_201_CREATED, response_model=Vehicle_Out)
def create_vehicle(request: Request, vehicle: Vehicle = Body(...), current_user: User_Out = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    vehicle = jsonable_encoder(vehicle)
    
    # check is vehicle is in the database, if yes respond with 'Vehicle already exists'
    if check_vehicle_make(vehicle["make"]) is not None:  

        vehicle_dict = request.app.database["vehicles"].find_one(
            {"make": vehicle["make"]}
        )

        vehicle_models_update = combine_lists(vehicle_dict["models"], vehicle["models"])
            
        request.app.database["vehicles"].update_one(
            {"make": vehicle["make"]},
            {"$set": { "models" : vehicle_models_update} }
        )

        updated_vehicle = request.app.database["vehicles"].find_one(
            {"make": vehicle["make"]}
        )
        return updated_vehicle

    new_vehicle = request.app.database["vehicles"].insert_one(vehicle)
    created_vehicle = request.app.database["vehicles"].find_one(
        {"_id": new_vehicle.inserted_id}
    )
    return created_vehicle

@router.get("/", response_description="List all vehicles", response_model=List[Vehicle_Out])
def list_vehicles(request: Request, current_user: User_Out = Depends(get_current_user)):
    vehicles = list(request.app.database["vehicles"].find(limit=100))
    return vehicles

# get one vehicle by id
@router.get("/{id}", response_description="Get a vehicle by id", response_model=Vehicle_Out)
def find_vehicle(id: str, request: Request, current_user: User_Out = Depends(get_current_user)):
    if (vehicle := request.app.database["vehicles"].find_one({"_id": ObjectId(id)})) is not None:
        return vehicle
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehicle with ID {id} not found")

# delete a vehicle by id
@router.delete("/{id}", response_description="Delete a vehicle")
def delete_vehicle(id: str, request: Request, response: Response, current_user: User_Out = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    delete_result = request.app.database["vehicles"].delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vehicle with ID {id} not found")

# There is no patch route for vehicles, I believe that combining 
# post and patch routes is a better approach for this case - see post route above