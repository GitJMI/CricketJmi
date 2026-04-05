# CricketJMI — Backend

A Flask-based REST API with real-time Socket.IO support for the CricketJMI live-streaming platform.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask |
| Database | PostgreSQL (via Supabase) |
| ORM | Flask-SQLAlchemy + Flask-Migrate |
| Auth | Flask-JWT-Extended (JWT Bearer tokens) |
| Real-time | Flask-SocketIO + Eventlet |
| Serialization | Marshmallow |
| CORS | Flask-CORS |
| Production Server | Gunicorn |

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── config.py            # Config loaded from .env
│   ├── extensions.py        # db, migrate, jwt singletons
│   ├── middleware/
│   ├── models/
│   │   ├── user_model.py
│   │   ├── channel_model.py
│   │   ├── message_model.py
│   │   └── subscription_model.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── channel_routes.py
│   │   ├── chat_routes.py
│   │   ├── subscription_routes.py
│   │   └── watch_routes.py
│   ├── schemas/
│   ├── services/
│   ├── sockets/
│   │   └── socket.py        # Socket.IO event handlers
│   └── utils/
│       └── decorators.py    # subscription_required, etc.
├── migrations/
├── run.py                   # Dev entry point
├── wsgi.py                  # Production (Gunicorn) entry point
├── requirements.txt
└── .env                     # Environment variables (not committed)
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Supabase / PostgreSQL credentials
user=your_db_user
password=your_db_password
host=your_supabase_host
port=5432
dbname=your_db_name

# JWT & Flask
JWT_SECRET_KEY=your_jwt_secret
SECRET_KEY=your_flask_secret
```

> SSL (`sslmode=require`) is enforced automatically for Supabase connections.

---

## Getting Started

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run database migrations

```bash
flask db upgrade
```

### 4. Start the development server

```bash
python run.py
```

The server starts at `http://127.0.0.1:5000`.

> For production, use Gunicorn via `wsgi.py`.

---

## Data Models

### `users`
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| username | String(100) | Unique |
| email | String(255) | Unique |
| password_hash | Text | Bcrypt hash |
| role | Enum | `client` \| `admin` |
| created_at | DateTime | UTC |

### `channels`
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| external_id | String(100) | |
| name | String(100) | |
| type | String(20) | Default: `iframe` |
| iframe_url | Text | Embed URL |
| is_active | Boolean | Default: `true` |

### `messages`
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | FK → users |
| channel_id | Integer | FK → channels |
| message | Text | |
| created_at | DateTime | UTC |

### `subscriptions`
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | FK → users |
| plan | String(50) | `basic` \| `premium` |
| start_date | DateTime | UTC |
| end_date | DateTime | |
| status | String(20) | `active` \| `expired` |

---

## REST API Reference

Base URL (development): `http://127.0.0.1:5000`

All protected endpoints require:
```
Authorization: Bearer <token>
```

---

### Auth — `/api/auth`

#### `POST /api/auth/register`
Register a new user.

**Body**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response `201`**
```json
{
  "message": "User registered successfully",
  "token": "<jwt>"
}
```

> Returns `400` if already logged in (valid JWT sent).

---

#### `POST /api/auth/login`
Authenticate and receive a JWT.

**Body**
```json
{
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response `200`**
```json
{
  "token": "<jwt>"
}
```

> Returns `400` if already logged in.

---

### Channels — `/api/channels`

#### `GET /api/channels/`
List all channels.

- **No auth**: returns only active channels.
- **Admin JWT**: returns all channels (including hidden ones).

**Response `200`**
```json
[
  {
    "id": 1,
    "name": "Star Sports 1",
    "type": "iframe",
    "is_active": true
  }
]
```

---

#### `GET /api/channels/<channel_id>`
Get a single channel (including `iframe_url`).

- Hidden channels return `403` for non-admins.

**Response `200`**
```json
{
  "id": 1,
  "name": "Star Sports 1",
  "type": "iframe",
  "iframe_url": "https://..."
}
```

---

#### `PUT /api/channels/<channel_id>` ⚠️ Admin only
Update a channel's name or visibility.

**Headers**: `Authorization: Bearer <admin_token>`

**Body** (any subset)
```json
{
  "name": "New Name",
  "is_active": false
}
```

**Response `200`**
```json
{
  "message": "Channel updated successfully",
  "channel": {
    "id": 1,
    "name": "New Name",
    "type": "iframe",
    "is_active": false
  }
}
```

---

### Chat — `/api/chat`

#### `GET /api/chat/<channel_id>/messages`
Fetch today's chat messages for a channel (paginated).

**Headers**: `Authorization: Bearer <token>` (required)

**Query params**

| Param | Default | Description |
|---|---|---|
| limit | 10 | Number of messages to return |
| offset | 0 | Number of messages to skip |

**Response `200`**
```json
[
  {
    "id": 42,
    "user_id": 7,
    "username": "johndoe",
    "message": "What a shot!",
    "created_at": "2026-04-05T07:30:00Z"
  }
]
```

> Messages are scoped to **today in IST (UTC+5:30)** and returned in chronological order (oldest → newest).

---

### Subscriptions — `/api/subscription`

#### `POST /api/subscription/buy`
Activate a subscription plan.

**Headers**: `Authorization: Bearer <token>`

**Body**
```json
{
  "plan": "basic"
}
```

**Response `201`**
```json
{
  "message": "Subscription activated",
  "plan": "basic",
  "expires_at": "2026-05-05T00:00:00"
}
```

---

#### `GET /api/subscription/status`
Check if the current user has an active subscription.

**Headers**: `Authorization: Bearer <token>`

**Response `200`**
```json
{
  "active": true
}
```

---

## Socket.IO Reference

Connect to the same base URL as the REST API.

### Events emitted by the **client**

| Event | Payload | Auth |
|---|---|---|
| `join` | `{ channel_id, token? }` | Optional |
| `leave` | `{ channel_id }` | — |
| `send_message` | `{ channel_id, token, message }` | Required |

### Events emitted by the **server**

| Event | Payload | Description |
|---|---|---|
| `online_users` | `{ channel_id, count }` | Sent to room on join/leave |
| `receive_message` | `{ user_id, username, message }` | Broadcast to room |
| `error` | `{ msg }` | Auth or rate-limit errors |

**Notes:**
- Guests (no token) can join rooms and view messages but **cannot send messages**.
- A **2-second cooldown** is enforced per user between messages.
- Messages are persisted to the `messages` table on every send.

---

## JWT Payload

The JWT includes the following custom claims:

```json
{
  "sub": "7",
  "role": "admin",
  "username": "johndoe",
  "email": "john@example.com"
}
```

---

## Admin Access

To promote a user to admin, use the helper script at the project root:

```bash
python promote_admin.py
```

---

## Deployment

The project is deployed on **Render**.

Production URL: `https://cricketjmi-backend.onrender.com`

Use `wsgi.py` as the entry point:
```bash
gunicorn wsgi:app
```
