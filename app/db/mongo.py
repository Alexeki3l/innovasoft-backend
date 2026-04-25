from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

if os.getenv("DEBUG", None) is None:
    path=os.path.dirname(__file__)[:-3]
    path_env= os.path.join(path, ".env")
    load_dotenv(dotenv_path=path_env)


client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))

db = client["innovasoft_local"]