from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db = client["parking_db"]
    return db
