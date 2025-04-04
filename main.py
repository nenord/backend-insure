from fastapi import FastAPI, Depends, HTTPException, Response # type: ignore
from pymongo import MongoClient # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore

from routers import users, vehicles, policies
from models import User_Out
from helpers import verify_password, create_access_token, find_user_email, get_current_user

from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware
config = dotenv_values(".env")

app = FastAPI()

origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(users.router)
app.include_router(vehicles.router)
app.include_router(policies.router)

@app.get("/")
async def root():
    return {"message": "Pay by mile car insurance API!"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    login_exception = HTTPException(status_code=400, detail="Incorrect username or password")
    user = find_user_email(form_data.username, app = app.database)
    if not verify_password(form_data.password, user['password_hash']):
       raise login_exception
    access_token = create_access_token( data={"sub": str(user['_id'])} )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/whoami")
async def who_am_i(current_user: User_Out = Depends(get_current_user)):        
    return current_user