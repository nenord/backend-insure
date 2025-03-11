# This file contains the routes for the vehicles endpoint
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder

from models import Vehicle
from helpers import check_vehicle_make, check_vehicle_model

import sys
sys.path.append("..")

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    responses={404: {"description": "Not found"}}
)

# Add a post route that will create a vehicle in the database
@router.post("/", response_description="Create a new vehicle", status_code=status.HTTP_201_CREATED, response_model=Vehicle)
def create_vehicle(request: Request, vehicle: Vehicle = Body(...)):
    vehicle = jsonable_encoder(vehicle)
    # check is vehicle is in the database, if yes respond with 'Vehicle already exists'
    if check_vehicle_make(vehicle["make"]) is not None:  
        if check_vehicle_model(vehicle["make"], vehicle["models"][0]) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vehicle already exists")

        vehicle_dict = request.app.database["vehicles"].find_one(
            {"make": vehicle["make"]}
        )
         
        vehicle_dict["models"].append(vehicle["models"][0])
            
        request.app.database["vehicles"].update_one(
            {"make": vehicle["make"]},
            {"$set": { "models" : vehicle_dict["models"]} }
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