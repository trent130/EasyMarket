import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):  # Adjust this as needed
            print(f'{event.src_path} has been modified, restarting Daphne...')
            self.restart_server()

    def restart_server(self):
        # Command to run your Daphne server
        subprocess.run(['daphne', 'myproject.asgi:application'])  # Adjust to your ASGI app location

if __name__ == "__main__":
    path = '.'  # The directory to watch
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
