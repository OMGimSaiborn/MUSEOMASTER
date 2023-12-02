from fastapi import APIRouter, HTTPException, Depends, Response
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson import json_util
from models import TicketSale, TicketType
from bson import ObjectId
from typing import List
from pydantic import BaseModel
from db import get_db

tickets_collection_name = "boletos"
employee_collection_name = "empleados"

ticket_router = APIRouter(prefix="/tickets", tags=["Tickets"])

class TicketInDB(BaseModel):
    ticket: TicketType
    _id: ObjectId

#Ruta para crear un tipo de boleto
@ticket_router.post("/tickets/create", response_model=TicketInDB)
def create_ticket(ticket: TicketType, db = Depends(get_db)):
  try:
    # Guardar el tipo de boleto en la base de datos
    tickets_collection = db[tickets_collection_name]
    result = tickets_collection.insert_one(ticket.model_dump())
    
    # Obtener el ID asignado por MongoDB
    inserted_id = result.inserted_id
    
    # Devolver el tipo de boleto creado junto con su ID
    return TicketInDB(ticket=ticket, _id=inserted_id)
  except Exception as e:
    print(e)
    raise e

# Obtener todos los Tickets
@ticket_router.get("/tickets/all")
def get_all_tickets(db = Depends(get_db)):
  try:
    tickets_collection = db[tickets_collection_name]
    return list(tickets_collection.find())
  except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail="Error al obtener los boletos")
    
# Obtener detalles de un boleto específico
@ticket_router.get("/tickets/{ticket_id}", response_model=TicketType)
def get_ticket(ticket_id: str, res = Response, db = Depends(get_db)):
  tickets_collection = db[tickets_collection_name]
  ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
  if not ticket:
    res.status_code = 404
    raise HTTPException(status_code=404, detail="Boleto no encontrado")

  # Convertir el _id a cadena
  ticket["_id"] = str(ticket["_id"])

  return TicketType(name="a", description="b", price=1)  # Crear una instancia de TicketType con los datos encontrados
