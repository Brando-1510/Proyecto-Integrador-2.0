import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD=os.getenv("PASSWORD")
DATABASE_URL=os.getenv("DATABASE_URL")