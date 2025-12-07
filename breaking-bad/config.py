import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Atlas URI should be set in .env or environment variables
    # Example: mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable is not set. Please set it to your MongoDB Atlas connection string.")
    DB_NAME = "news_classifier"
    COLLECTION_NAME = "news_items"
    
    FEED_DIR = os.path.join("data", "feed")
    RECIPIENTS_DIR = os.path.join("data", "recipients")
    ERROR_DIR = os.path.join("data", "error")
    
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Agent specific settings could go here
    MODEL_NAME = "gemini-1.5-flash"
