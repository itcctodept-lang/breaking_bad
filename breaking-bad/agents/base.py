import google.generativeai as genai
from config import Config
from database import Database
import logging
import json
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_name, prompt_template):
        self.agent_name = agent_name
        self.prompt_template = prompt_template
        self.db = Database()
        
        if not Config.GOOGLE_API_KEY:
             logging.warning("GOOGLE_API_KEY not set. LLM features will fail.")
        else:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.MODEL_NAME)

    def _get_llm_response(self, content):
        """Helper to call LLM with error handling."""
        try:
            prompt = self.prompt_template.format(content=content)
            response = self.model.generate_content(prompt)
            # Expecting JSON output from most agents, so we'll try to parse it safely
            # Ideally, we should enforce JSON mode in the prompt or API if available
            text = response.text.strip()
            # Basic cleanup if the model wraps json in markdown code blocks
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            return json.loads(text)
        except Exception as e:
            logging.error(f"Error in {self.agent_name}: {e}")
            return {"error": str(e)}

    def process(self, news_item):
        """
        Main processing method.
        1. Reads current state (though passed in, we might want to refresh).
        2. Generates result.
        3. Updates DB.
        """
        logging.info(f"Agent {self.agent_name} processing article {news_item['_id']}")
        
        result = self.execute(news_item)
        
        # Update MongoDB with this agent's result, sharing state
        # using dot notation to update specific agent field
        cleaned_result = self._sanitize_mongo_keys(result)
        
        self.db.get_collection().update_one(
            {"_id": news_item["_id"]},
            {"$set": {f"agents_results.{self.agent_name}": cleaned_result}}
        )
        return cleaned_result

    def _sanitize_mongo_keys(self, data):
        """Recursively replace keys containing '.' or start with '$' which Mongo forbids."""
        if isinstance(data, dict):
            return {k.replace('.', '_').replace('$', '_'): self._sanitize_mongo_keys(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_mongo_keys(i) for i in data]
        else:
            return data

    @abstractmethod
    def execute(self, news_item):
        """Specific logic for the agent. Must return a dict."""
        pass
