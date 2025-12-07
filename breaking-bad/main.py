import time
import os
import logging
from config import Config
from orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting News Classification System...")
    orchestrator = Orchestrator()
    
    # Ensure directories exist
    os.makedirs(Config.FEED_DIR, exist_ok=True)
    os.makedirs(Config.RECIPIENTS_DIR, exist_ok=True)
    os.makedirs(Config.ERROR_DIR, exist_ok=True)
    
    logging.info(f"Monitoring {Config.FEED_DIR} for new files...")
    
    try:
        while True:
            files = [f for f in os.listdir(Config.FEED_DIR) if f.endswith('.txt')]
            
            for file in files:
                file_path = os.path.join(Config.FEED_DIR, file)
                logging.info(f"Found new file: {file}")
                orchestrator.process_file(file_path)
            
            time.sleep(5)  # Poll every 5 seconds
            
    except KeyboardInterrupt:
        logging.info("Shutting down...")

if __name__ == "__main__":
    main()
