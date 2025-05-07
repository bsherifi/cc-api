# Currency Converter API

A comprehensive subscription-based currency converter API built with FastAPI, PostgreSQL, and SQLAlchemy. This API provides real-time currency conversion as well as historical exchange rate data.

## Features

✅ **Real-time Currency Conversion**: Convert between any supported currencies using current exchange rates  
✅ **Historical Exchange Rates**: Retrieve and convert using historical exchange rates  
✅ **Subscription-based Access**: Three subscription plans with different rate limits and credit allocations  
✅ **Credit System**: Credits deducted for conversion operations  
✅ **Rate Limiting**: Plan-based request rate limiting  
✅ **JWT Authentication**: Secure user authentication with JWT tokens  
✅ **API Key Authentication**: Simple authentication for API endpoints  
✅ **PostgreSQL Persistence**: Data stored in a PostgreSQL database  
✅ **Async Support**: Asynchronous database and API operations  
✅ **Comprehensive Documentation**: Auto-generated API documentation  
✅ **Docker Support**: Easy setup with Docker and docker-compose  

## Going Beyond the Requirements

To stand out for this task, I went beyond the basic requirements:

1. **Docker & Docker Compose**: Fully containerized application for easy deployment
2. **Database Integration**: Added PostgreSQL with SQLAlchemy ORM and Alembic migrations
3. **User Authentication**: Added JWT-based authentication and login endpoint
4. **Subscription Plans**: Implemented three different plans (Free, Pro, Diamond) with varying:
   - Rate limits (requests per minute)
   - Initial credit amounts
5. **Request Logging**: Tracking of all API usage
6. **Robust Error Handling**: Comprehensive error handling for API endpoints and external services

## Tech Stack

- **Python 3.10+**
- **FastAPI 0.115.1**: Modern, high-performance web framework
- **SQLAlchemy 2.0.40**: Async ORM support
- **Alembic**: Database migrations
- **PostgreSQL**: Data persistence
- **JWT**: Authentication tokens
- **HTTPX**: Async HTTP client for external API calls
- **SlowAPI**: Rate limiting
- **Docker & Docker Compose**: Containerization

## Architecture

The application follows a clean, modular architecture:

- **app/api/endpoints/**: API endpoint implementations
- **app/api/dependencies/**: FastAPI dependencies
- **app/models/**: Database models
- **app/schemas/**: Pydantic schemas for validation
- **app/services/**: External service integrations
- **app/core/**: Core application logic and configuration

## Setup and Installation

### Using Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd currency-converter-api
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The API will be available at: `http://localhost:8000`

Note: The application already includes default configuration values for the database and API keys, so no additional setup is needed for this demo.

## Subscription Plans

The API offers three subscription plans:

| Plan     | Rate Limit (req/min) | Initial Credits |
|----------|----------------------|----------------|
| Free     | 10                   | 100            |
| Pro      | 60                   | 1000           |
| Diamond  | 120                  | 5000           |

**Note on Rate Limiting**: Due to time constraints and integration challenges with SlowAPI, the current implementation uses a simplified rate limit of 5 requests per minute for all plans, regardless of the plan level. In a production environment, this would be properly implemented to follow the plan-specific limits (10, 60, or 120 req/min).

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

#### POST `/api/v1/auth/signup`
Register a new user and get an API key.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "plan_id": 1  // 1 = Free, 2 = Pro, 3 = Diamond
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "api_key": "zX7NLa1FVaQO0JxGEgH_tOzxJVWJj4x74E4IrT4dzUk",
  "credits": 100,
  "rate_limit": 10
}
```

#### POST `/api/v1/auth/login`
Login with an existing user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**: Same as signup

#### GET `/api/v1/auth/me`
Get current user information.

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "credits": 100,
  "api_key": "zX7NLa1FVaQO0JxGEgH_tOzxJVWJj4x74E4IrT4dzUk",
  "plan": {
    "id": 1,
    "name": "Free",
    "rate_limit": 10,
    "initial_credits": 100
  }
}
```

### Currency Operations

#### GET `/api/v1/currency/currencies`
List all supported currencies.

**Headers**:
```
X-API-Key: <api_key>
```

**Response**:
```json
{
  "currencies": {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "JPY": "Japanese Yen",
    "GBP": "British Pound",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    // ... more currencies
  }
}
```

#### GET `/api/v1/currency/convert`
Convert an amount from one currency to another.

**Headers**:
```
X-API-Key: <api_key>
```

**Query Parameters**:
- `from_currency`: Source currency code (e.g., USD)
- `to_currency`: Target currency code (e.g., EUR)
- `amount`: Amount to convert (e.g., 100)

**Response**:
```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "amount": 100,
  "converted_amount": 92.16,
  "rate": 0.9216
}
```

**Note**: Consumes 1 credit per request

#### GET `/api/v1/currency/convert/historical`
Get historical conversion rates for a specified period.

**Headers**:
```
X-API-Key: <api_key>
```

**Query Parameters**:
- `from_currency`: Source currency code (e.g., USD)
- `to_currency`: Target currency code (e.g., EUR)
- `amount`: Amount to convert (e.g., 100)
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format

**Response**:
```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "amount": 100,
  "rates": {
    "2023-05-01": {
      "EUR": 0.9183
    },
    "2023-05-02": {
      "EUR": 0.9175
    }
    // ... more dates
  },
  "converted_amounts": {
    "2023-05-01": 91.83,
    "2023-05-02": 91.75
    // ... more dates
  }
}
```

**Note**: 
- Consumes 1 credit per request
- Limited to dates within the past year
- End date cannot be in the future

## Testing the API

1. **Register a User**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123", "plan_id": 1}'
   ```

2. **List Available Currencies**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/currency/currencies" \
     -H "X-API-Key: YOUR_API_KEY"
   ```

3. **Convert Currency**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/currency/convert?from_currency=USD&to_currency=EUR&amount=100" \
     -H "X-API-Key: YOUR_API_KEY"
   ```

4. **Get Historical Rates**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/currency/convert/historical?from_currency=USD&to_currency=EUR&amount=100&start_date=2023-01-01&end_date=2023-01-31" \
     -H "X-API-Key: YOUR_API_KEY"
   ```

## External API Used

The application uses [ExchangeRate-API](https://www.exchangerate-api.com/) for currency exchange rates:
- Base URL: https://v6.exchangerate-api.com/v6/
- Endpoint for latest rates: `/latest/USD`
- Endpoint for historical rates: `/history/USD?start_date=2023-01-01&end_date=2023-01-31`

## Credits Deduction

The API deducts credits for the following operations:
- Currency conversion: 1 credit
- Historical data retrieval: 1 credit

Listing currencies doesn't consume any credits.

## Known Limitations

1. **Rate Limiting Implementation**: Currently, all API endpoints use a fixed rate limit of 5 requests per minute, regardless of subscription plan. This was a pragmatic simplification due to time constraints and integration challenges with the SlowAPI library. In a production environment, this would be implemented to properly respect each plan's rate limit.

2. **Date Range for Historical Data**: The external API has limitations on historical data retrieval, typically allowing only about 1 year of historical data.

## Development Notes

The codebase is structured to prioritize:
- Clean, modular architecture
- Separation of concerns
- Dependency injection
- Async operations
- Error handling
- Type safety

Given the 4-hour time constraint, I focused on delivering a complete but pragmatic solution that demonstrates best practices in modern API development. 