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

class MuseumRoomType(BaseModel):
    room_name: str
    exhibits: List[str]
    capacity: int
    description: str
    is_accessible: bool
    multimedia_guide_available: bool
    maintenance: str

class Activity(BaseModel):
    name: str
    type: str
    room: str #Relacionar la habitacion de museo
    nameGroup: str

#RELACIONADOS CON BOLETO

class TicketType(BaseModel):
    type: str
    description: str
    price: float

class FullTicketType(TicketType):
    id: str
    
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