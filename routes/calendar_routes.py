from fastapi import APIRouter, Depends
from pymongo.collection import Collection
from db import get_db
from datetime import date
from typing import List, Dict

calendar_router = APIRouter(prefix="/calendars", tags=["Calendar"])

def get_events_collection(db=Depends(get_db)) -> Collection:
    return db["eventos"]

@calendar_router.get("/all-dates/", response_model=List[Dict[str, str]])
def get_all_dates(
    events_collection: Collection = Depends(get_events_collection),
):
    all_dates = []

    for event in events_collection.find():
        event_data = {
            "date": event["date"].date().isoformat(),
            "title": event["title"]
        }
        all_dates.append(event_data)

    return all_dates
