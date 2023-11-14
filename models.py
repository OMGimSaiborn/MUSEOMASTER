from pydantic import BaseModel, EmailStr
from typing import List

# RELACIONADOS CON EL EMPLEADO
class BookingEmployee(BaseModel):
    name: str
    curp: str
    puesto: str
    cv: str
    foto: str

class Employee(BookingEmployee):
    rfc: str
    area: str
    formacion: List[str]
    experiencia: str
    # curp : str
    # fingerprint : str
    # foto : str
    # puesto : str
    # cv : str

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

class TicketSale(BaseModel):
    employee_id: str
    ticket_type: str
    quantity: int
    total_price: float

class TicketType(BaseModel):
    name: str
    description: str
    price: float

#RELACIONADS CON USUARIO

class User(BaseModel):
    username: str
    password: str
    email: str
    purchases: List[TicketSale] = []
