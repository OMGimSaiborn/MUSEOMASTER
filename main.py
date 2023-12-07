from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.ticket_routes import ticket_router
from routes.employee_routes import employee_router
# from routes import ticket_routes, employee_routes, event_routes

# Crear la aplicación
app = FastAPI(responses={404: {"detail": "Item not found"}})

# Configurar CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Maneja errores de validacion de datos al hacer solicitudes
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)

# Incluir las rutas
app.include_router(ticket_router)
app.include_router(employee_router)
# app.include_router(event_routes.app)
