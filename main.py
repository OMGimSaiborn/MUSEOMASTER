from fastapi import FastAPI, Depends
from routes.ticket_routes import ticket_router

# from routes import ticket_routes, employee_routes, event_routes
from fastapi.middleware.cors import CORSMiddleware
from db import get_db

# Crear la aplicación
app = FastAPI(responses={404: {"detail": str}})
get_db()
# Configurar CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(ticket_router)
# app.include_router(employee_routes.app)
# app.include_router(event_routes.app)