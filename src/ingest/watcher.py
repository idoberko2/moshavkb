import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.ingest.parser import parse_pdf
from src.db.chroma import add_document
import os

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith('.pdf'):
            self.process_file(event.src_path)

    def process_file(self, filepath):
        print(f"New PDF detected: {filepath}")
        # Give a small delay for file copy completion
        time.sleep(1) 
        
        try:
            doc_data = parse_pdf(filepath)
            if doc_data:
                add_document(doc_data)
                print(f"Successfully processed and indexed: {filepath}")
            else:
                print(f"Failed to process: {filepath}")
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")

def start_watching(dir_path):
    event_handler = PDFHandler()
    observer = Observer()
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        
    observer.schedule(event_handler, dir_path, recursive=False)
    observer.start()
    print(f"Watching directory: {dir_path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
