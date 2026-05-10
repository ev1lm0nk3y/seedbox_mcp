# Seedbox MCP Server

This is a Model Context Protocol (MCP) server designed to run on your seedbox. It provides tools to manage Deluge, trigger rsync syncs to your Synology, and monitor Sonarr/Radarr/Prowlarr/Jackett.

## Features
- **Deluge:** List, add, remove, pause, resume torrents.
- **Rsync:** Trigger push syncs to `your-fileserver.example.com`.
- **Arrs:** Check status of Sonarr, Radarr, Prowlarr, and Jackett.

## Setup
1.  **Profiles:** Edit `profiles.json` to add users. Each user needs:
    - `name`: Identifier for the user.
    - `token`: Unique Bearer token for authentication.
    - `rsync_destination`: The remote fileserver (e.g., `rsync://user@host:port/module` or `user@host`).
    - `rsync_port`: SSH port (if using SSH).
    - `rsync_remote_path`: Base path on the remote server.
    - `rsync_local_path`: Base path on the seedbox.
2.  **Environment:** Edit the `.env` file with your correct API keys and tokens.
3.  **Deployment:**
    - Copy the `seedbox_mcp` directory to your seedbox.
    - Run `docker-compose up -d --build`.
4.  **Authentication:** The server uses Bearer token authentication. Each user must include their specific `Authorization: Bearer <token>` header. Tools like `rsync` will automatically use the profile associated with the token.

## MCP Tools
- `deluge_list_torrents`
- `deluge_add_torrent(url)`
- `trigger_sync(category?)`
- `get_sync_status`
- `get_app_status(app)`
