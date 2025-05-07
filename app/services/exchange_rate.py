import httpx
import json
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from app.core.config import settings


class ExchangeRateService:
    """Service for interacting with the Exchange Rate API."""
    
    def __init__(self):
        self.api_key = settings.EXCHANGE_API_KEY
        self.base_url = settings.EXCHANGE_API_BASE_URL
        
    async def get_currencies(self) -> Dict[str, str]:
        """Get the list of supported currencies."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}{self.api_key}/codes")
                
                if response.status_code != 200:
                    raise Exception(f"API returned status code {response.status_code}")
                
                data = response.json()
                
                if data["result"] != "success":
                    raise Exception(f"API Error: {data.get('error', 'Unknown error')}")
                
                # Convert the list of currency codes and names to a dictionary
                currencies = {}
                for code, name in data["supported_codes"]:
                    currencies[code] = name
                    
                return currencies
            except json.JSONDecodeError:
                raise Exception(f"Invalid JSON response from API: {response.text}")
            except Exception as e:
                raise Exception(f"Currency API error: {str(e)}")
    
    async def get_latest_rate(self, from_currency: str, to_currency: str) -> float:
        """Get the latest exchange rate from one currency to another."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}{self.api_key}/latest/{from_currency}")
                
                if response.status_code != 200:
                    raise Exception(f"API returned status code {response.status_code}")
                
                data = response.json()
                
                if data["result"] != "success":
                    raise Exception(f"API Error: {data.get('error', 'Unknown error')}")
                
                # Get the conversion rate
                conversion_rates = data["conversion_rates"]
                if to_currency not in conversion_rates:
                    raise Exception(f"Currency {to_currency} not supported")
                
                return conversion_rates[to_currency]
            except json.JSONDecodeError:
                raise Exception(f"Invalid JSON response from API: {response.text}")
            except Exception as e:
                raise Exception(f"Rate API error: {str(e)}")
    
    async def get_historical_rates(
        self, 
        from_currency: str,
        to_currency: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Dict[str, float]]:
        """Get historical exchange rates for a period."""
        # Make sure end_date is not in the future
        today = date.today()
        if end_date > today:
            print(f"Adjusting end_date from {end_date} to {today} (cannot request future rates)")
            end_date = today
            
        # Limit the date range to avoid API limitations
        # This API typically allows a maximum range of 1 year
        if start_date < today - timedelta(days=365):
            start_date = today - timedelta(days=365)
            print(f"Adjusting start_date to {start_date} (API limit of 1 year of history)")
            
        # Format the dates as strings (YYYY-MM-DD)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        print(f"Requesting historical rates from {start_date_str} to {end_date_str}")
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}{self.api_key}/history/{from_currency}"
                params = {"start_date": start_date_str, "end_date": end_date_str}
                print(f"Making API request to: {url} with params: {params}")
                
                response = await client.get(url, params=params)
                print(f"API response status: {response.status_code}")
                
                if response.status_code != 200:
                    return self._handle_error_response(response)
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    raise Exception(f"Invalid JSON response from API: {response.text}")
                
                print(f"API response result: {data.get('result', 'no result field')}")
                
                if data["result"] != "success":
                    error_msg = f"API Error: {data.get('error', 'Unknown error')}"
                    print(error_msg)
                    if data.get('error') == "unsupported_date":
                        error_msg += ". The API may not support data this far back."
                    elif "time_frame" in str(data.get('error', '')).lower():
                        error_msg += ". The time frame is too large for this API."
                    raise Exception(error_msg)
                
                # Extract the historical rates
                historical_rates = {}
                for date_str, rates in data["conversion_rates"].items():
                    if to_currency in rates:
                        if date_str not in historical_rates:
                            historical_rates[date_str] = {}
                        historical_rates[date_str][to_currency] = rates[to_currency]
                
                print(f"Retrieved rates for {len(historical_rates)} dates")
                return historical_rates
                
        except Exception as e:
            print(f"Error in get_historical_rates: {str(e)}")
            raise Exception(f"Failed to get historical rates: {str(e)}")
    
    def _handle_error_response(self, response):
        """Handle error responses from the API."""
        if response.status_code == 404:
            # For 404 errors, return an empty result set rather than failing
            print(f"API returned 404, returning empty result set")
            return {}
        else:
            # For other errors, raise an exception
            try:
                error_data = response.json()
                error_detail = error_data.get('error', 'Unknown error')
            except:
                error_detail = response.text or f"HTTP {response.status_code}"
            
            raise Exception(f"API error: {error_detail}")


# Create a singleton instance of the service
exchange_rate_service = ExchangeRateService() 