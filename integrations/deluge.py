import os
from deluge_client import DelugeRPCClient
from dotenv import load_dotenv

load_dotenv()

class DelugeClient:
    def __init__(self):
        self.host = os.getenv("DELUGE_RPC_HOST", "127.0.0.1")
        self.port = int(os.getenv("DELUGE_RPC_PORT", "58846"))
        self.user = os.getenv("DELUGE_RPC_USER")
        self.password = os.getenv("DELUGE_RPC_PASS")
        self.client = DelugeRPCClient(self.host, self.port, self.user, self.password)

    def get_torrents(self):
        self.client.connect()
        try:
            return self.client.call('core.get_torrents_status', {}, ['name', 'progress', 'state', 'save_path', 'total_size', 'eta'])
        finally:
            self.client.disconnect()

    def add_torrent(self, url):
        self.client.connect()
        try:
            if url.startswith("magnet:"):
                return self.client.call('core.add_torrent_magnet', url, {})
            else:
                return self.client.call('core.add_torrent_url', url, {})
        finally:
            self.client.disconnect()

    def remove_torrent(self, torrent_id, remove_data=False):
        self.client.connect()
        try:
            return self.client.call('core.remove_torrent', torrent_id, remove_data)
        finally:
            self.client.disconnect()

    def pause_torrent(self, torrent_id):
        self.client.connect()
        try:
            return self.client.call('core.pause_torrent', [torrent_id])
        finally:
            self.client.disconnect()

    def resume_torrent(self, torrent_id):
        self.client.connect()
        try:
            return self.client.call('core.resume_torrent', [torrent_id])
        finally:
            self.client.disconnect()
