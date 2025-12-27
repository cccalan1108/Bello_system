from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Database settings - Neon PostgreSQL connection string
    # Format: postgresql://user:password@host:port/database?sslmode=require
    DATABASE_URL = os.getenv('DATABASE_URL', '')

    # Server settings
    SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8800'))
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'bello-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')