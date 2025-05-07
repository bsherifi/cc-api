from datetime import date
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class Currency(BaseModel):
    code: str
    name: str


class CurrencyList(BaseModel):
    currencies: Dict[str, str]


class ConversionRequest(BaseModel):
    from_currency: str = Field(..., description="Currency code to convert from")
    to_currency: str = Field(..., description="Currency code to convert to")
    amount: float = Field(..., description="Amount to convert")
    start_date: Optional[date] = Field(None, description="Start date for historical data")
    end_date: Optional[date] = Field(None, description="End date for historical data")


class ConversionRate(BaseModel):
    rate: float
    date: Optional[date] = None


class ConversionResult(BaseModel):
    from_currency: str
    to_currency: str
    amount: float
    converted_amount: float
    rate: float
    date: Optional[date] = None


class HistoricalConversionResult(BaseModel):
    from_currency: str
    to_currency: str
    amount: float
    rates: Dict[str, Dict[str, float]]  # Date -> {currency: rate}
    converted_amounts: Dict[str, float]  # Date -> converted amount 