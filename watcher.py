import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import signal
import psutil


class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.server_process = None
        self.start_server()
    
    def start_server(self):
        """Start the Daphne server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        print("Starting Daphne server...")
        self.server_process = subprocess.Popen([
            'daphne', '-p', '8000', 'students.asgi:application'
        ])
        print("Daphne server started on port 8000")

    def on_modified(self, event):
        """Called when a file is modified. Only restart for relevant Python files."""
        if (event.src_path.endswith('.py') and 
            not event.src_path.endswith('__pycache__') and
            not '/migrations/' in event.src_path and
            not event.src_path.endswith('.pyc')):
            print(f'{event.src_path} has been modified, restarting Daphne...')
            self.restart_server()

    def restart_server(self):
        """Restart the Daphne server efficiently"""
        if self.server_process:
            try:
                # Gracefully terminate the process
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                self.server_process.kill()
                self.server_process.wait()
        
        # Small delay before restart
        time.sleep(0.5)
        self.start_server()

    def stop_server(self):
        """Stop the server when shutting down"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()


if __name__ == "__main__":
    path = '.'  # The directory to watch
    event_handler = ReloadHandler()
    observer = Observer()
    
    # Only watch specific directories for better performance
    watch_paths = [
        'users/',
        'marketplace/',
        'products/',
        'orders/',
        'payment/',
        'staticpages/',
        'students/'
    ]
    
    for watch_path in watch_paths:
        if os.path.exists(watch_path):
            observer.schedule(event_handler, watch_path, recursive=True)
            print(f"Watching: {watch_path}")
    
    observer.start()
    print("File watcher started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        observer.stop()
        event_handler.stop_server()
    observer.join()
