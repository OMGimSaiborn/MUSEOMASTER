from fastapi import APIRouter, HTTPException, Depends
from models import TicketType, FullTicketType
from bson import ObjectId
from typing import List
from pydantic import BaseModel
from db import get_db

tickets_collection_name = "boletos"

ticket_router = APIRouter(prefix="/tickets", tags=["Tickets"])

class TicketInDB(BaseModel):
  ticket: TicketType
  _id: ObjectId

#Ruta para crear un tipo de boleto
@ticket_router.post("/create", response_model=TicketInDB)
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
@ticket_router.get("/all", response_model=List[FullTicketType])
def get_all_tickets(db = Depends(get_db)):
  try:
    tickets_collection = db[tickets_collection_name]
    tickets = list(tickets_collection.find())
    for ticket in tickets:
      ticket["id"] = str(ticket["_id"])
    return tickets
  except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail="Error al obtener los boletos")
    
# Obtener detalles de un boleto específico
@ticket_router.get("/{ticket_id}", response_model=FullTicketType)
def get_ticket(ticket_id: str,  db = Depends(get_db)):
  tickets_collection = db[tickets_collection_name]
  ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
  if not ticket:
    raise HTTPException(status_code=404, detail="Boleto no encontrado")

  # Convertir el _id a cadena
  ticket["id"] = str(ticket["_id"])

  return ticket  # Crear una instancia de TicketType con los datos encontrados
