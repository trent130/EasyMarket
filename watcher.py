import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DAPHNE_CMD = ['daphne', '-b', '0.0.0.0', '-p', '8000', 'students.asgi:application']

server_process = None


def start_server():
    global server_process
    if server_process and server_process.poll() is None:
        print('Stopping previous server...')
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    print('Starting Daphne...')
    server_process = subprocess.Popen(DAPHNE_CMD)


class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            print(f'Changed: {event.src_path} — reloading...')
            start_server()


if __name__ == '__main__':
    print('Starting dev watcher...')
    start_server()

    path = '.'
    observer = Observer()
    observer.schedule(ReloadHandler(), path, recursive=True)
    observer.start()
    print('Watching for .py changes. Press Ctrl+C to stop.')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        if server_process and server_process.poll() is None:
            server_process.terminate()
