from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson import json_util
from models import TicketSale, TicketType
from bson import ObjectId
from typing import List
from pydantic import BaseModel

app = APIRouter()

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["MUSEOMASTER"]
collection_tickets = db["boletos"]
collection_employees = db["empleados"]

app = APIRouter()

class TicketInDB(BaseModel):
    ticket: TicketType
    _id: ObjectId

#Ruta para crear un tipo de boleto
@app.post("/tickets/create", response_model=TicketInDB)
async def create_ticket(ticket: TicketType):
    # Guardar el tipo de boleto en la base de datos
    result = collection_tickets.insert_one(ticket.dict())
    
    # Obtener el ID asignado por MongoDB
    inserted_id = result.inserted_id
    
    # Devolver el tipo de boleto creado junto con su ID
    return TicketInDB(ticket=ticket, _id=inserted_id)

# Obtener todos los Tickets
@app.get("/tickets/all", response_model=List[TicketType])
async def get_all_tickets():
    tickets = list(collection_tickets.find())
    return tickets

# Obtener detalles de un boleto específico
@app.get("/tickets/{ticket_id}", response_model=TicketType)
async def get_ticket(ticket_id: str):
    ticket = collection_tickets.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Convertir el _id a cadena
    ticket["_id"] = str(ticket["_id"])

    return TicketType(**ticket)  # Crear una instancia de TicketType con los datos encontrados