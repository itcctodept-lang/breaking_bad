import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Cohere API Configuration
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    if not COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY environment variable is not set. Please set it in your .env file.")
    
    COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Recipient List
    VALID_RECIPIENTS = [
        "Legal",
        "HR",
        "PR",
        "Finance",
        "Engineering",
        "Executive",
        "All Employees"
    ]
    
    # MCP Server Configuration
    MCP_SERVER_NAME = "document-tools"
    MCP_SERVER_VERSION = "1.0.0"
