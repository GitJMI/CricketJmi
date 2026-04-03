# CricketJMI Backend

This is the Flask backend for the CricketJMI streaming and real-time chat application. It provides RESTful APIs for user authentication, channel management, subscriptions, and WebSocket integrations for real-time live chat.

## Tech Stack

- **Framework**: [Flask](https://flask.palletsprojects.com/)
- **Database**: PostgreSQL (hosted on [Supabase](https://supabase.com/))
- **ORM**: [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- **Migrations**: [Flask-Migrate](https://flask-migrate.readthedocs.io/)
- **Authentication**: [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- **Real-time WebSockets**: [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- **Server**: [Eventlet](https://eventlet.net/)

## Prerequisites

- **Python 3.8+**
- **PostgreSQL** database (or Supabase project)

## Installation and Setup

### 1. Clone the repository and navigate to the backend
```bash
cd backend
```

### 2. Create and activate a Virtual Environment
**Windows**:
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the root of the `backend` directory based on the following template:

```env
# Database Credentials (e.g., from Supabase)
user=your_db_user
password=your_db_password
host=your_db_host (Use connection pooler host if on Supabase, e.g., aws-0-xxx.pooler.supabase.com)
port=6543
dbname=postgres

# Secret Keys
JWT_SECRET_KEY=your_super_secret_jwt_key
SECRET_KEY=your_flask_secret_key
```

## Running the Application

To start the Flask development server with SocketIO enabled, simply run:

```bash
python run.py
```
The server will start running at `http://127.0.0.1:5000/`.

## Database Migrations

This project uses Flask-Migrate (Alembic) to handle database schema changes. When you create or update models, run the following commands:

**Initialize migrations (Only once if `migrations` folder doesn't exist):**
```bash
flask db init
```

**Create a migration script for new changes:**
```bash
flask db migrate -m "Added users table"
```

**Apply migrations to the database:**
```bash
flask db upgrade
```

## API Endpoints Overview

The backend exposes several modular API blueprints:

- **Authentication (`/api/auth`)**:
  - `POST /api/auth/register` - Create a new user.
  - `POST /api/auth/login` - Authenticate a user and receive a JWT.
- **Channels (`/api/channels`)**: Handle live streaming channel data (CRUD/Visibility).
- **Subscriptions (`/api/subscription`)**: Manage user subscriptions/billing.
- **Chat (`/api/chat`)**: Retrieve past chat records or messages.

## Real-Time Sockets overview

Real-time chat is powered by Socket.IO (`app.sockets.socket`). Ensure clients connect to the root URL or namespace for real-time bidirectional communication.

## Project Structure

```
backend/
├── .env                # Environment variables
├── run.py              # Main entry point to run the server
├── app/                # Main application package
│   ├── __init__.py     # App factory and blueprint registration
│   ├── config.py       # Configuration and env variables loader
│   ├── extensions.py   # Setup db, migrate, jwt dependencies
│   ├── models/         # SQLAlchemy models (tables)
│   ├── routes/         # API Route definitions
│   ├── services/       # Core business logic
│   ├── sockets/        # Socket.IO handlers
│   └── utils/          # Helper modules and tools
├── migrations/         # Auto-generated database migrations
└── requirements.txt    # Python dependencies
```
