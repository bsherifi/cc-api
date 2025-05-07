from datetime import date, datetime, timedelta
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.api_key import get_api_user
from app.api.dependencies.credits import require_credits
from app.api.dependencies.rate_limit import limiter
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, RequestLog
from app.schemas.currency import CurrencyList, ConversionRequest, ConversionResult, HistoricalConversionResult
from app.services.exchange_rate import exchange_rate_service

router = APIRouter()


@router.get("/currencies", response_model=CurrencyList)
@limiter.limit("1000/day")
async def get_currencies(
    request: Request,
    user: User = Depends(get_api_user)
):
    """
    Get a list of all supported currencies.
    This endpoint doesn't consume credits.
    """
    try:
        currencies = await exchange_rate_service.get_currencies()
        return {"currencies": currencies}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def get_api_key(request: Request) -> str:
    """Extract API key from request headers"""
    return request.headers.get("x-api-key", "none")


@router.get("/convert", response_model=ConversionResult)
@limiter.limit("5 per minute", key_func=get_api_key)
async def convert_currency(
    request: Request,
    from_currency: str = Query(..., description="Currency code to convert from"),
    to_currency: str = Query(..., description="Currency code to convert to"),
    amount: float = Query(..., description="Amount to convert"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_credits(settings.CREDITS_PER_CONVERSION))
):
    """
    Convert an amount from one currency to another.
    Consumes 1 credit per request.
    """
    try:
        # Get the conversion rate
        rate = await exchange_rate_service.get_latest_rate(from_currency, to_currency)
        
        # Calculate the converted amount
        converted_amount = amount * rate
        
        # Log the request
        log = RequestLog(
            user_id=user.id,
            endpoint="/convert",
            request_data=f"from={from_currency}, to={to_currency}, amount={amount}",
            response_data=f"rate={rate}, converted_amount={converted_amount}",
            status_code=200,
            credits_deducted=settings.CREDITS_PER_CONVERSION
        )
        db.add(log)
        await db.commit()
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "converted_amount": converted_amount,
            "rate": rate,
            "date": None  # Current date is implied
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/convert/historical", response_model=HistoricalConversionResult)
@limiter.limit("5 per minute", key_func=get_api_key)
async def convert_historical(
    request: Request,
    from_currency: str = Query(..., description="Currency code to convert from"),
    to_currency: str = Query(..., description="Currency code to convert to"),
    amount: float = Query(..., description="Amount to convert"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD), must be within the last year"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD), cannot be in the future"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_credits(settings.CREDITS_PER_HISTORICAL))
):
    """
    Get historical conversion rates for a specified period.
    Consumes 1 credit per request.
    
    Note: This API only supports historical data from the past year.
    The end date cannot be in the future.
    """
    try:
        # Validate dates
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before or equal to end date"
            )
        
        # Automatically adjust date ranges for better user experience
        today = date.today()
        
        # Handle future end dates
        original_end_date = end_date
        if end_date > today:
            end_date = today
        
        # Handle start dates too far in the past
        original_start_date = start_date
        max_history = today - timedelta(days=365)
        if start_date < max_history:
            start_date = max_history
        
        # Get historical rates
        try:
            historical_rates = await exchange_rate_service.get_historical_rates(
                from_currency, to_currency, start_date, end_date
            )
            
            # If we got an empty result and dates were adjusted, let the user know
            if not historical_rates:
                # If both dates were adjusted
                if original_start_date != start_date and original_end_date != end_date:
                    note = f"Note: Your dates were adjusted from {original_start_date} - {original_end_date} to {start_date} - {end_date} to comply with API limits."
                # If only start date was adjusted
                elif original_start_date != start_date:
                    note = f"Note: Your start date was adjusted from {original_start_date} to {start_date} because the API only provides data for the past year."
                # If only end date was adjusted
                elif original_end_date != end_date:
                    note = f"Note: Your end date was adjusted from {original_end_date} to {end_date} because future dates are not available."
                else:
                    note = "No historical data found for this date range and currency pair."
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No historical data available. {note}"
                )
            
        except Exception as e:
            if "404" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No historical data available for this currency pair and date range."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Exchange rate API error: {str(e)}"
                )
        
        # Calculate converted amounts for each date
        converted_amounts = {}
        for date_str, rates in historical_rates.items():
            if to_currency in rates:
                converted_amounts[date_str] = amount * rates[to_currency]
        
        # Log the request
        log = RequestLog(
            user_id=user.id,
            endpoint="/convert/historical",
            request_data=f"from={from_currency}, to={to_currency}, amount={amount}, "
                         f"start_date={start_date}, end_date={end_date}",
            response_data=f"dates_returned={len(historical_rates)}",
            status_code=200,
            credits_deducted=settings.CREDITS_PER_HISTORICAL
        )
        db.add(log)
        await db.commit()
        
        # Add a note about date adjustment for the response
        result = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "rates": historical_rates,
            "converted_amounts": converted_amounts
        }
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        ) 