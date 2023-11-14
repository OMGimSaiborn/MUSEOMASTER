from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson import json_util
from models import User, TicketSale

app = APIRouter()

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["MUSEOMASTER"]
collection_users = db["users"]
