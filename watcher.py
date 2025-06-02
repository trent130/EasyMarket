import os
import time
import signal
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import threading
from typing import Optional


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, command: list[str], watch_extensions: list[str] = None):
        """
        Initialize the reload handler.
        
        Args:
            command: Command to run the server (e.g., ['daphne', '-p', '8000', 'students.asgi:application'])
            watch_extensions: File extensions to watch (default: ['.py'])
        """
        self.command = command
        self.watch_extensions = watch_extensions or ['.py']
        self.server_process: Optional[subprocess.Popen] = None
        self.restart_lock = threading.Lock()
        self.last_restart = 0
        self.restart_delay = 2  # Minimum seconds between restarts
        self.ignore_patterns = {
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'node_modules',
            '.pytest_cache',
            'migrations'  # Optional: ignore Django migrations
        }

    def should_ignore_path(self, path: str) -> bool:
        """Check if the path should be ignored."""
        path_obj = Path(path)
        
        # Check if any parent directory is in ignore patterns
        for part in path_obj.parts:
            if part in self.ignore_patterns:
                return True
                
        # Check file extension
        if not any(path.endswith(ext) for ext in self.watch_extensions):
            return True
            
        return False

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory or self.should_ignore_path(event.src_path):
            return

        # Debounce rapid file changes
        current_time = time.time()
        if current_time - self.last_restart < self.restart_delay:
            return

        rel_path = os.path.relpath(event.src_path)
        print(f'📝 {rel_path} modified, restarting server...')
        self.restart_server()

    def on_created(self, event):
        """Called when a file is created."""
        if not event.is_directory and not self.should_ignore_path(event.src_path):
            rel_path = os.path.relpath(event.src_path)
            print(f'➕ {rel_path} created, restarting server...')
            self.restart_server()

    def on_deleted(self, event):
        """Called when a file is deleted."""
        if not event.is_directory and not self.should_ignore_path(event.src_path):
            rel_path = os.path.relpath(event.src_path)
            print(f'🗑️  {rel_path} deleted, restarting server...')
            self.restart_server()

    def restart_server(self):
        """Restart the server by killing the old process and starting a new one."""
        with self.restart_lock:
            try:
                # Kill existing server process
                if self.server_process and self.server_process.poll() is None:
                    print("🔄 Stopping existing server...")
                    self.server_process.terminate()
                    try:
                        self.server_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print("⚠️  Force killing server...")
                        self.server_process.kill()
                        self.server_process.wait()

                # Start new server process
                print(f"🚀 Starting server: {' '.join(self.command)}")
                self.server_process = subprocess.Popen(
                    self.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Combine stderr with stdout
                    universal_newlines=True,
                    bufsize=1  # Line buffered
                )
                
                self.last_restart = time.time()
                print(f"✅ Server started with PID: {self.server_process.pid}")
                
                # Start a thread to monitor server output
                threading.Thread(
                    target=self._monitor_server_output,
                    daemon=True
                ).start()

            except Exception as e:
                print(f"❌ Error restarting server: {e}")

    def _monitor_server_output(self):
        """Monitor server output and print it with prefixes."""
        if not self.server_process:
            return
            
        try:
            for line in iter(self.server_process.stdout.readline, ''):
                if line.strip():
                    print(f"[SERVER] {line.strip()}")
                    
            # Process has ended
            if self.server_process.poll() is not None:
                return_code = self.server_process.returncode
                if return_code != 0:
                    print(f"⚠️  Server exited with code {return_code}")
                    
        except Exception as e:
            print(f"❌ Error monitoring server output: {e}")

    def start_initial_server(self):
        """Start the initial server."""
        print("🚀 Starting initial server...")
        self.restart_server()

    def cleanup(self):
        """Clean up server process on exit."""
        if self.server_process and self.server_process.poll() is None:
            print("🛑 Shutting down server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️  Force killed server")


def setup_signal_handlers(handler: ReloadHandler, observer: Observer):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        observer.stop()
        handler.cleanup()
        observer.join()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main function to run the auto-reload server."""
    # Configuration
    WATCH_PATH = '.'
    WATCH_EXTENSIONS = ['.py', '.html', '.css', '.js']  # Add more as needed
    SERVER_COMMAND = ['daphne', '-p', '8000', 'students.asgi:application']
    
    # You can also make this configurable via command line args
    if len(sys.argv) > 1:
        WATCH_PATH = sys.argv[1]
    
    # Create event handler and observer
    event_handler = ReloadHandler(
        command=SERVER_COMMAND,
        watch_extensions=WATCH_EXTENSIONS
    )
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    
    # Set up signal handlers
    setup_signal_handlers(event_handler, observer)
    
    # Start initial server
    event_handler.start_initial_server()
    
    # Start file watcher
    observer.start()
    
    abs_path = os.path.abspath(WATCH_PATH)
    print(f"👀 Watching for changes in {abs_path}")
    print(f"📁 Extensions: {', '.join(WATCH_EXTENSIONS)}")
    print("💡 Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass  # Handled by signal handler


if __name__ == "__main__":
    main()