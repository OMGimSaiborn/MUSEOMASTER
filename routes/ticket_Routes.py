from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson import json_util
from models import TicketSale, TicketType
from bson import ObjectId

app = APIRouter()

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["MUSEOMASTER"]
collection_ticket_types = db["ticket_types"]
collection_sales = db["sales"]
