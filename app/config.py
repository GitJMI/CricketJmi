import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()


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