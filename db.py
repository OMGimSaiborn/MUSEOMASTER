import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
    
def get_db():
  try:
    db_name = os.getenv("DB_NAME")
    yield client.get_database(db_name)
  except Exception as e:
    print(e)
    raise e
  