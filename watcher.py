import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess


class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        """ Called when a file is modified. If the modified file is a
        Python source file, restart the Daphne server. """
        if event.src_path.endswith('.py'):  # Adjust this as needed
            print(f'{event.src_path} has been modified, restarting Daphne...')
            self.restart_server()

    def restart_server(self):
        # Command to run your Daphne server
        """
        Restart the Daphne server.

        This method is called when the source files are modified. It is
        responsible for restarting the Daphne server. The actual command
        to run the server is specified in the code below.

        """
        subprocess.run(['daphne', 'students.asgi:application'])  # Adjust to your ASGI app location


time.sleep(1)  # Wait for the server to restart
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
