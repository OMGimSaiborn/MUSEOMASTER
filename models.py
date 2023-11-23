from pydantic import BaseModel
from typing import List

# RELACIONADOS CON EL EMPLEADO
class Employee(BaseModel):
    name: str
    curp: str
    puesto: str
    cv: str
    foto: str
    email : str
    rfc: str
    area: str
    formacion: List[str]
    experiencia: str
    event_info: List[dict] = []

# RELACIONADOS CON EL MUSEO
class MapMuseum(BaseModel):
    map: str
    lastUpdate: str
    author: str

class Room(BaseModel):
    name: str

class Activity(Room):
    name: str
    type: str
    room: str
    nameGroup: str

class Space(BaseModel):
    type: str
    name: str
    location: str

#RELACIONADOS CON BOLETO

class TicketType(BaseModel):
    name: str
    description: str
    price: float
class TicketSale(BaseModel):
    employee_id: str
    ticket_type: TicketType
    quantity: int
    total_price: float

#MODELOS DE EVENTOS
class Event(BaseModel):
    title: str
    description: str
    date: str
    location: str
    image_url: str
    organizer_id: str 