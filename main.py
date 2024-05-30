from datetime import date, datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BeforeValidator, ValidationError, WrapValidator

# Здесь можно задать подробную информацию об ошибках валидации,
# если это потребуется
VALIDATION_ERRORS = []

ALLOWED_DATE_FORMATS: List[str] = ["%d.%m.%Y", ]

MIN_DEPOSIT_PERIODS = 1
MAX_DEPOSIT_PERIODS = 60

MIN_DEPOSIT_AMOUNT = 10000
MAX_DEPOSIT_AMOUNT = 3000000

MIN_DEPOSIT_RATE = 1
MAX_DEPOSIT_RATE = 8


def date_parser(val):
    if isinstance(val, str):
        for fmt in ALLOWED_DATE_FORMATS:
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        raise ValidationError.from_exception_data(
            "Wrong description: deposit date parser", line_errors=VALIDATION_ERRORS)
    if isinstance(val, date):
        return val
    raise ValidationError("Wrong description: deposit date parser")


def validate_deposit_periods(val, handler):
    if MIN_DEPOSIT_PERIODS <= handler(val) <= MAX_DEPOSIT_PERIODS:
        return handler(val)
    raise ValidationError.from_exception_data(
        "Wrong description:  deposit periods range", line_errors=VALIDATION_ERRORS)


def validate_deposit_amount(val, handler):
    if MIN_DEPOSIT_AMOUNT <= handler(val) <= MAX_DEPOSIT_AMOUNT:
        return handler(val)
    raise ValidationError.from_exception_data(
        "Wrong description: amount amount range", line_errors=VALIDATION_ERRORS)


def validate_deposit_rate(val, handler):
    if MIN_DEPOSIT_RATE <= handler(val) <= MAX_DEPOSIT_RATE:
        return handler(val)
    raise ValidationError.from_exception_data(
        "Wrong description: deposit rate range", line_errors=VALIDATION_ERRORS)


deposit_rate_validator = WrapValidator(validate_deposit_rate)
deposit_amount_validator = WrapValidator(validate_deposit_amount)
deposit_periods_validator = WrapValidator(validate_deposit_periods)


class DescriptionItem(BaseModel):
    dt: Annotated[date, BeforeValidator(date_parser), "Дата заявки"]
    periods: Annotated[int, deposit_periods_validator, "Количество месяцев по вкладу"]
    amount: Annotated[int, deposit_amount_validator, "Сумма вклада"]
    rate: Annotated[float, deposit_rate_validator, "Процент по вкладу"]


app = FastAPI()
router = APIRouter()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Описание ошибка"},
    )


@router.post("/deposit-calc/", status_code=status.HTTP_200_OK)
def deposit_calc(description_item: Annotated[DescriptionItem, Depends()]):
    print("some calculations")
    return {"message": "Calculation completed"}


app.include_router(router)
