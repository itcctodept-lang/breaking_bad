import hashlib
import os
import shutil
import json
import logging
from datetime import datetime
from config import Config
from database import Database
from agents.classifiers import (
    UrgencyAgent, SensitivityAgent, TopicAgent, TypeAgent, RecipientAgent
)
from agents.finalizer import FinalizerAgent

class Orchestrator:
    def __init__(self):
        self.db = Database()
        self.agents = [
            UrgencyAgent(),
            SensitivityAgent(),
            TopicAgent(),
            TypeAgent(),
            RecipientAgent()
        ]
        self.finalizer = FinalizerAgent()

    def process_file(self, file_path):
        logging.info(f"Orchestrator received file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {e}")
            return

        filename = os.path.basename(file_path)
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Initialize News Item in DB
        news_item = {
            "_id": file_hash,
            "filename": filename,
            "content": content,
            "status": "processing",
            "agents_results": {},
            "created_at": datetime.now()
        }
        self.db.save_news_item(news_item)

        # Run Process Agents
        # In a real distributed system, these could be async/parallel tasks
        for agent in self.agents:
            try:
                agent.process(news_item)
                # Refresh news_item from DB to get updates (simulating shared state)
                news_item = self.db.get_news_item(file_hash)
            except Exception as e:
                logging.error(f"Agent {agent.agent_name} failed: {e}")

        # Run Finalizer
        try:
            final_result = self.finalizer.process(news_item)
            
            # Update item with final decision
            self.db.get_collection().update_one(
                {"_id": file_hash},
                {
                    "$set": {
                        "final_decision": final_result,
                        "status": "completed"
                    }
                }
            )
            news_item = self.db.get_news_item(file_hash)
            
            self._distribute(news_item, file_path)

        except Exception as e:
            logging.error(f"Finalizer failed: {e}")
            self.db.get_collection().update_one(
                 {"_id": file_hash},
                 {"$set": {"status": "error", "error": str(e)}}
            )
            self._move_to_error(file_path)

    def _distribute(self, news_item, original_file_path):
        final = news_item.get("final_decision", {})
        recipients = final.get("final_recipients", [])
        
        if not recipients:
            logging.warning(f"No recipients for {news_item['filename']}. Moving to error.")
            self._move_to_error(original_file_path)
            return

        # Prepare metadata
        metadata = {
            "original_filename": news_item["filename"],
            "id": news_item["_id"],
            "metadata": final
        }
        
        # Distribute to each recipient
        for recipient in recipients:
            recipient_dir = os.path.join(Config.RECIPIENTS_DIR, self._slugify(recipient))
            os.makedirs(recipient_dir, exist_ok=True)
            
            # Copy article
            dest_file = os.path.join(recipient_dir, news_item["filename"])
            shutil.copy2(original_file_path, dest_file)
            
            # Save metadata
            meta_filename = news_item["filename"] + ".json"
            with open(os.path.join(recipient_dir, meta_filename), 'w') as f:
                json.dump(metadata, f, indent=2)
                
        # Remove from feed after successful distribution
        os.remove(original_file_path)
        logging.info(f"Successfully processed and distributed {news_item['filename']}")

    def _move_to_error(self, file_path):
        dest = os.path.join(Config.ERROR_DIR, os.path.basename(file_path))
        shutil.move(file_path, dest)

    def _slugify(self, text):
        return text.lower().replace(" ", "_").replace("/", "-")
