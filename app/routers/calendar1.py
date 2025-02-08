from fastapi import APIRouter
from fastapi import HTTPException
import requests

router = APIRouter()

@router.get("/calendar/{year}/{month}/{day}", tags=["Calendar"])
async def get_calendar(year: int, month: int, day: int):
    url = f"https://holidayapi.ir/jalali/{year}/{month}/{day}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Return the fetched data
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching calendar data")
