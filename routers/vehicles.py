# This file contains the routes for the vehicles endpoint
from fastapi import APIRouter, Body, Request, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder   
from typing import List

from models import Vehicle, User_Out, Vehicle_Out
from helpers import check_vehicle_make, get_current_user, combine_lists

import sys
sys.path.append("..")

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    responses={404: {"description": "Not found"}}
)

# Add a post route that will create a vehicle in the database
@router.post("/", response_description="Create a new vehicle", status_code=status.HTTP_201_CREATED, response_model=Vehicle)
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
def list_vehiles(request: Request, current_user: User_Out = Depends(get_current_user)):
    if current_user:
        vehicles = list(request.app.database["vehicles"].find(limit=100))
        return vehicles
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")