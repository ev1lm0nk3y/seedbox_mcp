import os
import subprocess
from dotenv import load_dotenv
from auth import current_user

load_dotenv()

class RsyncManager:
    def __init__(self):
        # We'll fetch details from current_user during execution
        self._processes = {} # map user name to process

    def trigger_sync(self, category=None):
        profile = current_user.get()
        if not profile:
            return {"error": "No user profile found in context"}

        username = profile.get("name")
        if self.is_running(username):
            return {"error": "Sync already in progress for this user"}
        
        local_path = profile.get("rsync_local_path")
        remote_path = profile.get("rsync_remote_path")
        destination = profile.get("rsync_destination")
        port = profile.get("rsync_port", 22)

        if category:
            local_path = os.path.join(local_path, category)
            remote_path = os.path.join(remote_path, category)

        # Check if we should use rsync:// or ssh
        # User provided example: rsync://ryan@your-fileserver.example.com:2222/video/TV\ Shows/
        # Note: rsync:// doesn't usually use a port like :2222 in the same way SSH does.
        # If it's the rsync daemon, the URL format is rsync://[USER@]HOST[:PORT]/MODULE[/PATH]
        
        if destination.startswith("rsync://"):
            # It's already a URL
            cmd = [
                "rsync", "-rlux", "--progress", "--stats",
                local_path + "/",
                f"{destination}/{remote_path}/"
            ]
        else:
            # Assume SSH
            cmd = [
                "rsync", "-rux", "--partial", "--stats",
                "-e", f"ssh -p {port}",
                local_path + "/",
                f"{destination}:{remote_path}/"
            ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self._processes[username] = process
            return {"status": "Sync started", "pid": process.pid, "user": username}
        except Exception as e:
            return {"error": str(e)}

    def is_running(self, username):
        process = self._processes.get(username)
        if process is None:
            return False
        return process.poll() is None

    def get_status(self):
        profile = current_user.get()
        if not profile:
            return {"error": "No user profile found in context"}
        
        username = profile.get("name")
        process = self._processes.get(username)
        
        if process is None:
            return {"status": "Idle", "user": username}
        
        poll = process.poll()
        if poll is None:
            return {"status": "Running", "user": username}
        
        stdout, stderr = process.communicate()
        return {
            "status": "Completed" if poll == 0 else "Failed",
            "exit_code": poll,
            "user": username,
            "output": stdout[-1000:], # last 1000 chars
            "error": stderr
        }
