# AfriConnect Backend API

FastAPI-based backend for AfriConnect - An investment discovery platform connecting founders with investors.

## Features

- User authentication (Founder and Investor roles)
- Founder profile and traction tracking
- Investor discovery feed with filtering
- Partnership and connection management
- Direct messaging within partnerships
- JWT-based authentication

## Tech Stack

- **Framework**: FastAPI
- **Database ORM**: SQLModel
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Settings Management**: Pydantic Settings
- **Package Manager**: uv

## Setup

### Prerequisites

- Python 3.11+
- uv (Python package manager)

### Installation

1. Clone the repository
2. Install dependencies using uv:

```bash
uv sync
```

### Configuration

1. Copy `.env.example` to `.env`
2. Update environment variables as needed:

```bash
cp .env.example .env
```

Edit `.env` and change `SECRET_KEY` to a secure random string.

### Running the Application

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user

### Founder
- `GET /api/v1/founder/feed` - Get home feed
- `GET /api/v1/founder/traction` - Get traction metrics
- `GET /api/v1/founder/profile` - Get profile
- `PUT /api/v1/founder/profile` - Update profile

### Investor
- `GET /api/v1/investors/discover` - Discover startups
- `GET /api/v1/investors/saved` - Get saved founders
- `POST /api/v1/investors/saved/{startup_id}` - Save founder
- `DELETE /api/v1/investors/saved/{startup_id}` - Remove saved
- `PUT /api/v1/investors/saved/{startup_id}/note` - Update note
- `GET /api/v1/investors/profile` - Get profile
- `PUT /api/v1/investors/profile` - Update profile

### Partnership
- `POST /api/v1/partnerships/request-deck` - Request deck
- `POST /api/v1/partnerships/initiate` - Initiate partnership
- `GET /api/v1/partnerships` - Get partnerships
- `POST /api/v1/partnerships/{id}/accept` - Accept partnership
- `POST /api/v1/partnerships/{id}/message` - Send message

## Project Structure

```
app/
├── main.py              # Application entry point
├── config.py            # Settings configuration
├── database.py          # Database setup
├── models/              # SQLModel database models
├── schemas/             # Pydantic request/response schemas
├── api/v1/              # API route handlers
├── crud/                # Database CRUD operations
├── services/            # Business logic services
├── utils/               # Utilities (JWT, security, errors)
└── middleware/          # HTTP middleware

tests/                   # Test files
```

## Database Models

- **User**: Base user with email, password, and role
- **Founder**: Extended founder profile with startup details
- **Investor**: Extended investor profile with firm details
- **Partnership**: Connection between investor and founder
- **Message**: Direct messages within partnerships

## Authentication Flow

1. User signs up or logs in
2. Server returns JWT token and user info
3. Client includes token in Authorization header for subsequent requests
4. Token is validated on each protected endpoint

## Error Handling

The API returns standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Validation Error
- 500: Server Error

## Development

To install development dependencies:

```bash
uv sync --extra dev
```

Format code:
```bash
uv run black .
```

Lint code:
```bash
uv run ruff check .
```

Run tests:
```bash
uv run pytest
```
