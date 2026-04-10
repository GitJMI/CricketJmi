import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()


def _parse_csv_env(var_name, default=""):
    raw_value = os.getenv(var_name, default)
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


class Config:

    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")


    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SSL REQUIRED for Supabase
    # If using Transaction Pooler or Session Pooler, we want to ensure we disable SQLAlchemy client side pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
        "connect_args": {
            "sslmode": "require"
        }
    }


    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")

    SECRET_KEY = os.getenv("SECRET_KEY", "another-secret-key")

    CORS_ORIGINS = _parse_csv_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://cricketjmi.vercel.app",
    )
    SOCKET_CORS_ORIGINS = _parse_csv_env(
        "SOCKET_CORS_ORIGINS",
        ",".join(CORS_ORIGINS),
    )
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]