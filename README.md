# Youth Group Management System

CS125 Final Project by **Woman In Stem**

A full-stack application for managing youth group events, registrations, small groups, and attendance using FastAPI, React, MySQL, MongoDB, and Redis.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- MySQL
- MongoDB (optional, for event types and notes)
- Redis (optional, for live check-ins)

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database:**
   Create `backend/config.py` with your database credentials:
   ```python
   DB_USER = "root"
   DB_PASSWORD = "your_password"
   DB_HOST = "127.0.0.1"
   DB_PORT = 3306
   DB_NAME = "YouthGroupDB"
   MONGO_URI = "your_mongo_uri"
   MONGO_DB_NAME = "youthgroup_db"
   REDIS_HOST = "127.0.0.1"
   REDIS_PORT = 6379
   REDIS_PASSWORD = ""
   REDIS_USERNAME = ""
   REDIS_SSL = False
   ```

3. **Load database:**
   ```bash
   mysql -u root -p -h 127.0.0.1 < database/schema.sql
   mysql -u root -p -h 127.0.0.1 < database/data.sql
   ```

4. **Run backend:**
   ```bash
   uvicorn backend.main:app --reload --port 8099
   ```

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run frontend:**
   ```bash
   npm run dev
   ```

## Project Structure

```
WomenInStem/
├── backend/                    # Backend API code
│   ├── __init__.py
│   ├── main.py                # Main FastAPI app
│   ├── config.py              # Configuration
│   ├── database.py            # Database connections
│   ├── graphql/               # GraphQL API
│   │   ├── __init__.py
│   │   ├── schema.py          # GraphQL schema
│   │   └── app.py             # GraphQL router
│   └── models/                # Pydantic models (for future)
│       └── __init__.py
├── frontend/                  # React frontend (unchanged)
├── database/                  # SQL files
│   ├── schema.sql
│   └── data.sql
├── scripts/                   # Setup scripts
│   ├── setup_mongo.py
│   └── setup_redis.py
├── docs/                      # Documentation
│   ├── README.md
│   ├── ER_Diagram.pdf
│   └── PhotoOfInsomnia.png
├── README.md                  # Quick start guide
├── requirements.txt
└── Dockerfile
```

## Features

- **People Management**: Create, read, update, delete people
- **Event Management**: Schedule and manage events
- **Registrations**: Register attendees, leaders, and volunteers for events
- **Small Groups**: Manage small groups with members and leaders
- **Live Check-ins**: Real-time check-in system using Redis
- **Notes**: Person and event notes stored in MongoDB
- **GraphQL API**: Alternative to REST API for flexible data queries

## API Endpoints

- REST API: `http://localhost:8099`
- GraphQL API: `http://localhost:8099/graphql`
- API Documentation: `http://localhost:8099/docs`

## Technologies

- **Backend**: FastAPI, Python
- **Frontend**: React, Vite
- **Databases**: MySQL, MongoDB, Redis
- **API**: REST & GraphQL

## Team

**Woman In Stem**

For a more detailed documentation, see [docs/README.md](docs/README.md)

