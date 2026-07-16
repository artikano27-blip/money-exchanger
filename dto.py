import decimal
from dataclasses import dataclass

@dataclass
class CurrencyDTO:
    id:int
    name: str
    code: str
    sign: str

@dataclass
class ExchangeRatesDTO:
    id:int
    baseCurrency: CurrencyDTO
    targetCurrency: CurrencyDTO
    rate: decimal

@dataclass
class ExchangeResultDTO:
    baseCurrency: CurrencyDTO
    targetCurrency: CurrencyDTO
    rate: float
    amount: float
    convertedAmount: float