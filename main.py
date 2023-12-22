from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi import FastAPI
from routes.ticket_routes import ticket_router
from routes.employee_routes import employee_router
from routes.event_routes import event_router
from routes.room_routes import room_router
from routes.calendar_routes import calendar_router
from routes.ticket_routes import ticket_stats_router
from fastapi.middleware.cors import CORSMiddleware
from routes.binnacle_routes import binnacle_router

app = FastAPI(responses={404: {"detail": "Item not found"}})

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
app.include_router(event_router)
app.include_router(room_router)
app.include_router(calendar_router)
app.include_router(binnacle_router)
app.include_router(ticket_stats_router)


@app.get('/')
def hello():
    return {"Hello"}