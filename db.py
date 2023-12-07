import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME")
        client = MongoClient(uri, server_api=ServerApi('1'))
        yield client.get_database(db_name)
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e
    finally:
        client.close()
