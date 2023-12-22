from fastapi import APIRouter, HTTPException, Depends
from models import TicketType, FullTicketType, TicketCreateResponse
from bson import ObjectId
from typing import List, Dict, Union
from datetime import datetime, timedelta
from pymongo.collection import Collection
from db import get_db

tickets_collection_name = "boletos"

ticket_router = APIRouter(prefix="/tickets", tags=["Tickets"])
ticket_stats_router = APIRouter(prefix="/ticket-stats", tags=["Ticket Stats"])

# Ruta para crear un tipo de boleto
@ticket_router.post("/create", response_model=TicketCreateResponse)  
def create_ticket(ticket: TicketType, db=Depends(get_db)):
    try:
        tickets_collection = db[tickets_collection_name]
        result = tickets_collection.insert_one(ticket.dict())

        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Error al insertar el boleto en la base de datos")

        created_ticket = tickets_collection.find_one({"_id": result.inserted_id})

        if not created_ticket:
            raise HTTPException(status_code=500, detail="Error al obtener el boleto recién creado de la base de datos")

        created_ticket["id"] = str(created_ticket["_id"])

        success_message = {"message": "Boleto creado exitosamente", "ticket": created_ticket}
        return TicketCreateResponse(**success_message)
    except Exception as e:
        print(f"Error al crear el boleto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el boleto")

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

  ticket["id"] = str(ticket["_id"])

  return ticket

# Actualizar un boleto existente
@ticket_router.put("/update/{ticket_id}", response_model=FullTicketType)
def update_ticket(ticket_id: str, updated_ticket: TicketType, db=Depends(get_db)):
    tickets_collection = db[tickets_collection_name]
    existing_ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})
    
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Boleto no encontrado")

    updated_fields = updated_ticket.dict(exclude_unset=True)
    tickets_collection.update_one({"_id": ObjectId(ticket_id)}, {"$set": updated_fields})
    updated_ticket_db = tickets_collection.find_one({"_id": ObjectId(ticket_id)})

    updated_ticket_db["id"] = str(updated_ticket_db["_id"])

    return updated_ticket_db

# Eliminar un boleto existente
@ticket_router.delete("/delete/{ticket_id}", response_model=dict)
def delete_ticket(ticket_id: str, db=Depends(get_db)):
    tickets_collection = db[tickets_collection_name]
    deleted_ticket = tickets_collection.find_one_and_delete({"_id": ObjectId(ticket_id)})

    if not deleted_ticket:
        raise HTTPException(status_code=404, detail="Boleto no encontrado")

    deleted_ticket["id"] = str(deleted_ticket["_id"])

    return {"message": "Boleto eliminado", "deleted_ticket": deleted_ticket}
    
# Comprar boleto
@ticket_router.post("/buy/{ticket_id}", response_model=dict)
def buy_ticket(ticket_id: str, quantity: int, db=Depends(get_db)):
    try:
        tickets_collection = db[tickets_collection_name]
        existing_ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})

        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Boleto no encontrado")

        tickets_collection.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$inc": {"sold_quantity": quantity}}
        )

        purchase_info = (datetime.now(), quantity)
        tickets_collection.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$push": {"ticket_sales": purchase_info}}
        )

        return {"message": "Compra exitosa"}

    except Exception as e:
        print(f"Error al comprar boleto: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al comprar boleto")
    

#RUTAS PARA LAS ESTADISTICAS DE BOLETOS
    
# Obtener ganancias totales por tipo de boleto
@ticket_stats_router.get("/total-revenue", response_model=Dict[str, float])
def get_total_revenue(db=Depends(get_db)):
    try:
        tickets_collection = db["boletos"]

        tickets = list(tickets_collection.find())

        total_revenue = {}

        for ticket in tickets:
            ticket_type = ticket["type"]
            total_revenue[ticket_type] = total_revenue.get(ticket_type, 0) + ticket["price"] * ticket["sold_quantity"]

        return total_revenue

    except Exception as e:
        print(f"Error al obtener ganancias totales: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener ganancias totales")

# Obtener el mes con más ventas
@ticket_stats_router.get("/best-selling-month", response_model=Dict[str, Union[str, int]])
def get_best_selling_month(db=Depends(get_db)):
    try:
        tickets_collection = db["boletos"]

        tickets = list(tickets_collection.find())

        monthly_sales_count = {}

        for ticket in tickets:
            for sale_date, quantity in ticket.get("ticket_sales", []):
                month_key = sale_date.strftime("%Y-%m")
                monthly_sales_count[month_key] = monthly_sales_count.get(month_key, 0) + quantity

        best_selling_month = max(monthly_sales_count, key=monthly_sales_count.get)

        return {"best_selling_month": best_selling_month, "total_sales": monthly_sales_count[best_selling_month]}

    except Exception as e:
        print(f"Error al obtener el mes con más ventas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener el mes con más ventas")