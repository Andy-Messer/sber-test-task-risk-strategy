import decimal
import unittest

from app import (MAX_DEPOSIT_AMOUNT, MAX_DEPOSIT_PERIODS, MAX_DEPOSIT_RATE,
                 MIN_DEPOSIT_AMOUNT, MIN_DEPOSIT_PERIODS, MIN_DEPOSIT_RATE,
                 VALIDATION_ERRORS, app, date_parser, excel_round)
from fastapi.testclient import TestClient
from pydantic import ValidationError

DELTA = 1
SOME_INT_VALUE = 1
EPS = decimal.Decimal(1e-9)

EXAMPLE_VALIDATION_ERROR_DATE = ValidationError.from_exception_data(
    "Wrong description: deposit date parser",
    line_errors=VALIDATION_ERRORS
)

class TestValidators(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # Проверка некорректно введенной даты
    def test_deposit_calc_400_wrong_date_fmt(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "2021-01-31",
                "periods": 7,
                "amount": 10000,
                "rate": 6
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})
        
    # Проверка крайнего случая для парсера дат
    def test_date_parser_wrong_type(self):
        with self.assertRaises(TypeError) as context:
            date_parser(SOME_INT_VALUE)
            
        self.assertTrue('Wrong description: wrong date type' in str(context.exception))
    
    # Проверка нижней границы периода
    def test_deposit_calc_400_min_periods(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": MIN_DEPOSIT_PERIODS - DELTA,
                "amount": 10000,
                "rate": 6
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})
    
    # Проверка верхней границы периода
    def test_deposit_calc_400_max_periods(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": MAX_DEPOSIT_PERIODS + DELTA,
                "amount": 10000,
                "rate": 6
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})

    # Проверка нижней границы депозита
    def test_deposit_calc_400_min_amount(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": 7,
                "amount": MIN_DEPOSIT_AMOUNT - DELTA,
                "rate": 6
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})
    
    # Проверка верхней границы депозита
    def test_deposit_calc_400_max_amount(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": 7,
                "amount": MAX_DEPOSIT_AMOUNT + DELTA,
                "rate": 6
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})

    # Проверка нижней границы рейтинга
    def test_deposit_calc_400_min_rate(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": 7,
                "amount": 10000,
                "rate": MIN_DEPOSIT_RATE - DELTA
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})
    
    # Проверка верхней границы рейтинга
    def test_deposit_calc_400_max_rate(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": 7,
                "amount":  10000,
                "rate": MAX_DEPOSIT_RATE + DELTA
            },
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Описание ошибка"})
    
    
class TestDepositCalc(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    # Проверка корректной работы расчета
    def test_deposit_calc_correct(self):
        response = self.client.post(
            "/deposit-calc/",
            params={
                "dt": "31.01.2021",
                "periods": 7,
                "amount": 10000,
                "rate": 6
            },
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), \
            {
                '31.01.2021': 10050.0,
                '28.02.2021': 10100.25,
                '31.03.2021': 10150.75,
                '30.04.2021': 10201.51,
                '31.05.2021': 10252.51,
                '30.06.2021': 10303.78,
                '31.07.2021': 10355.29
            })
        
    def test_excel_round_main_case(self):
        a = decimal.Decimal(0.055)
        self.assertTrue(decimal.Decimal(0.06) - EPS <= excel_round(a, 2) <= decimal.Decimal(0.06) + EPS)
        
    # Проверка крайнего случая для округления в формате Excel
    def test_excel_round_0(self):
        a = None
        self.assertEqual(0, excel_round(a, 2))
        
if __name__ == '__main__':
    unittest.main()
    