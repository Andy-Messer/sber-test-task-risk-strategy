from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, status
from pydantic import BaseModel


class InvalidDescriptionException(Exception):
    "Raised when the input values are bad :("
    pass


class DescriptionItem(BaseModel):
    dt: Annotated[date, "Дата заявки"]
    periods: Annotated[int, "Количество месяцев по вкладу"]
    amount: Annotated[int, "Сумма вклада"]
    rate: Annotated[float, "Процент по вкладу"]


app = FastAPI()
router = APIRouter()


@router.post("/deposit-calc/", status_code=status.HTTP_200_OK)
def create_item(item: Annotated[DescriptionItem, Depends()]):
    print(item)
    print("some calculations")
    return {"message": "Calculation completed"}


app.include_router(router)
