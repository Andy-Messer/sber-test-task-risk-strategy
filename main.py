import decimal
from datetime import date, datetime
from typing import Annotated, List

import pandas as pd
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BeforeValidator, ValidationError, WrapValidator

# Здесь можно задать подробную информацию об ошибках валидации
VALIDATION_ERRORS = []


# Параметры валидации
ALLOWED_DATE_FORMATS: List[str] = ["%d.%m.%Y", ]

MIN_DEPOSIT_PERIODS = 1
MAX_DEPOSIT_PERIODS = 60

MIN_DEPOSIT_AMOUNT = 10000
MAX_DEPOSIT_AMOUNT = 3000000

MIN_DEPOSIT_RATE = 1
MAX_DEPOSIT_RATE = 8


PRECISION = 2


def date_parser(val):
    if isinstance(val, str):
        for fmt in ALLOWED_DATE_FORMATS:
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        raise ValidationError.from_exception_data(
            "Wrong description: deposit date parser", line_errors=VALIDATION_ERRORS
        )
    if isinstance(val, date):
        return val
    raise ValidationError("Wrong description: deposit date parser")


def validate_deposit_periods(val, handler):
    if MIN_DEPOSIT_PERIODS <= handler(val) < MAX_DEPOSIT_PERIODS:
        return handler(val)
    raise ValidationError.from_exception_data(
        "Wrong description:  deposit periods range", line_errors=VALIDATION_ERRORS
    )


def validate_deposit_amount(val, handler):
    if MIN_DEPOSIT_AMOUNT <= handler(val) <= MAX_DEPOSIT_AMOUNT:
        return handler(val)
    raise ValidationError.from_exception_data(
        "Wrong description: amount amount range", line_errors=VALIDATION_ERRORS
    )


def validate_deposit_rate(val, handler):
    if MIN_DEPOSIT_RATE <= handler(val) <= MAX_DEPOSIT_RATE:
        return handler(val)
    raise ValidationError.from_exception_data(
        "Wrong description: deposit rate range", line_errors=VALIDATION_ERRORS
    )


deposit_rate_validator = WrapValidator(validate_deposit_rate)
deposit_amount_validator = WrapValidator(validate_deposit_amount)
deposit_periods_validator = WrapValidator(validate_deposit_periods)


class DescriptionItem(BaseModel):
    dt: Annotated[date, BeforeValidator(date_parser), "Дата заявки"]
    periods: Annotated[int, deposit_periods_validator, "Количество месяцев по вкладу"]
    amount: Annotated[int, deposit_amount_validator, "Сумма вклада"]
    rate: Annotated[decimal.Decimal, deposit_rate_validator, "Процент по вкладу"]


app = FastAPI()
router = APIRouter()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Описание ошибка"},
    )


def excel_round(number: decimal.Decimal, digits: int) -> decimal.Decimal:
   if number is None or pd.isna(number):
        return decimal.Decimal(0)

   context = decimal.getcontext()
   context.rounding = decimal.ROUND_HALF_UP
   rounded_number = round(number, digits)
   return decimal.Decimal(rounded_number)


def return_calc(amount: int, rate: decimal.Decimal) -> decimal.Decimal:
    return amount * (1 + rate/12/100)


@router.post("/deposit-calc/", status_code=status.HTTP_200_OK)
async def deposit_calc(description_item: Annotated[DescriptionItem, Depends()]):
    results = []
    results.append(return_calc(description_item.amount, description_item.rate))
    
    for _ in range(description_item.periods - 1):
        results.append(return_calc(results[-1], description_item.rate))
        
    datelist = [date_val.date() for date_val in pd.date_range(description_item.dt, periods=description_item.periods, freq='ME')]
    results = [excel_round(result, PRECISION) for result in results]
    
    return {
        date.strftime("%d.%m.%Y"): result for date, result in zip(datelist, results)
    }


app.include_router(router)
