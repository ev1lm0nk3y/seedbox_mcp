import os
import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from dotenv import load_dotenv

from auth import AuthMiddleware
from integrations.deluge import DelugeClient
from integrations.rsync import RsyncManager
from integrations.arrs import ArrsClient

load_dotenv()

# Initialize integrations
deluge = DelugeClient()
rsync = RsyncManager()
sonarr = ArrsClient("SONARR")
radarr = ArrsClient("RADARR")
prowlarr = ArrsClient("PROWLARR")
jackett = ArrsClient("JACKETT")

app = Server("seedbox-mcp")

@app.list_tools()
async def list_tools() -> list[Any]:
    return [
        {
            "name": "deluge_list_torrents",
            "description": "List all torrents in Deluge with their status",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "deluge_add_torrent",
            "description": "Add a new torrent to Deluge via URL or Magnet link",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Torrent URL or Magnet link"}
                },
                "required": ["url"]
            }
        },
        {
            "name": "deluge_remove_torrent",
            "description": "Remove a torrent from Deluge",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "torrent_id": {"type": "string", "description": "ID of the torrent to remove"},
                    "remove_data": {"type": "boolean", "description": "Whether to also remove the downloaded data", "default": False}
                },
                "required": ["torrent_id"]
            }
        },
        {
            "name": "deluge_pause_torrent",
            "description": "Pause a torrent in Deluge",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "torrent_id": {"type": "string", "description": "ID of the torrent to pause"}
                },
                "required": ["torrent_id"]
            }
        },
        {
            "name": "deluge_resume_torrent",
            "description": "Resume a torrent in Deluge",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "torrent_id": {"type": "string", "description": "ID of the torrent to resume"}
                },
                "required": ["torrent_id"]
            }
        },
        {
            "name": "trigger_sync",
            "description": "Trigger rsync sync from seedbox to fileserver",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Optional category to sync (e.g. Movies, TV Shows)"}
                }
            }
        },
        {
            "name": "get_sync_status",
            "description": "Check the status of the current or last sync operation",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "get_app_status",
            "description": "Get the status of *arr applications",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "app": {"type": "string", "enum": ["sonarr", "radarr", "prowlarr", "jackett"]}
                },
                "required": ["app"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> Any:
    if name == "deluge_list_torrents":
        res = await asyncio.to_thread(deluge.get_torrents)
        return {"content": [{"type": "text", "text": str(res)}]}
    
    elif name == "deluge_add_torrent":
        res = await asyncio.to_thread(deluge.add_torrent, arguments["url"])
        return {"content": [{"type": "text", "text": f"Added torrent: {res}"}]}

    elif name == "deluge_remove_torrent":
        res = await asyncio.to_thread(deluge.remove_torrent, arguments["torrent_id"], arguments.get("remove_data", False))
        return {"content": [{"type": "text", "text": f"Removed torrent: {res}"}]}

    elif name == "deluge_pause_torrent":
        res = await asyncio.to_thread(deluge.pause_torrent, arguments["torrent_id"])
        return {"content": [{"type": "text", "text": f"Paused torrent: {res}"}]}

    elif name == "deluge_resume_torrent":
        res = await asyncio.to_thread(deluge.resume_torrent, arguments["torrent_id"])
        return {"content": [{"type": "text", "text": f"Resumed torrent: {res}"}]}
    
    elif name == "trigger_sync":
        res = await asyncio.to_thread(rsync.trigger_sync, arguments.get("category"))
        return {"content": [{"type": "text", "text": str(res)}]}
    
    elif name == "get_sync_status":
        res = await asyncio.to_thread(rsync.get_status)
        return {"content": [{"type": "text", "text": str(res)}]}
    
    elif name == "get_app_status":
        app_name = arguments["app"]
        client = {"sonarr": sonarr, "radarr": radarr, "prowlarr": prowlarr, "jackett": jackett}[app_name]
        res = await client.get_system_status()
        return {"content": [{"type": "text", "text": str(res)}]}
    
    raise ValueError(f"Unknown tool: {name}")

# Starlette setup for SSE
sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request.send) as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse.handle_post_messages),
    ]
)

# Add Auth Middleware
starlette_app.add_middleware(AuthMiddleware)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
