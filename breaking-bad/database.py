from pymongo import MongoClient
from pymongo.collection import Collection
from config import Config
import logging

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.DB_NAME]
            self.collection: Collection = self.db[Config.COLLECTION_NAME]
            logging.info(f"Connected to MongoDB at {Config.MONGO_URI}")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise e

    def get_collection(self) -> Collection:
        return self.collection

    def save_news_item(self, news_item: dict):
        return self.collection.replace_one(
            {"_id": news_item["_id"]}, 
            news_item, 
            upsert=True
        )

    def get_news_item(self, news_id: str):
        return self.collection.find_one({"_id": news_id})
        
    def close(self):
        self.client.close()
