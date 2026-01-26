from src.config import config
from src.ingest.watcher import start_watching
from src.db.chroma import get_collection

def main():
    print("Starting Moshav Knowledge Base Ingestion Service...")
    
    # Ensure DB connection works on startup
    get_collection()
    
    # Start watching folder
    start_watching(config.DOCUMENT_DIR)

if __name__ == "__main__":
    main()
