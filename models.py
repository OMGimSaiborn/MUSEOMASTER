from pydantic import BaseModel, Field
from typing import List, Union, Tuple
from bson import ObjectId
from datetime import datetime, date

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

class EmployeeInDB(BaseModel):
    _id: str
    name: str
    curp: str
    puesto: str
    cv: str
    foto: str
    email: str
    rfc: str
    area: str
    formacion: List[str]
    experiencia: str
    event_info: List[dict]

class User(BaseModel):
    id: str
    email: str
    name: str

class UserInDB(User):
    password: str

class EmployeeCreateResponse(BaseModel):
    message: str
    employee: EmployeeInDB

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
    
class MuseumRoomInDB(BaseModel):
    room: MuseumRoomType
    _id: str

#RELACIONADOS CON BOLETO

class TicketType(BaseModel):
    type: str
    description: str
    price: float
    ticket_sales: List[Tuple[datetime, int]] = []   
    sold_quantity: int = 0

class TicketInDB(BaseModel):
    ticket: TicketType
    _id: ObjectId

class FullTicketType(TicketType):
    id: str
    
class TicketCreateResponse(BaseModel):
    message: str
    ticket: Union[FullTicketType, None] = None

#MODELOS DE EVENTOS
class Event(BaseModel):
    title: str
    description: str
    date: date
    location: str
    image_url: str
    organizer_id: str 

class EventInDB(BaseModel):
    event: Event
    _id: ObjectId
    

class EventResponse(Event):
    organizer_id: str = Field(..., alias="_id")

class DeletedEventResponse(BaseModel):
    title: str
    type : str
    description: str
    date: date
    location: str
    organizer_id: str

    #BITACORAS DE ACCESO
class AccessBinnacle(BaseModel):
    employee_id: str
    location: str
    in_hour: datetime = Field(default_factory=datetime.now)
    out_hour: datetime
    activity: str
    description: str

class SuccessResponse(BaseModel):
    message: str