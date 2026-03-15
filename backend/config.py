import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_PATH = os.getenv("DB_PATH")
    ENV = os.getenv("FLASK_ENV", "production")

