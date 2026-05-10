import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class ArrsClient:
    def __init__(self, app_name):
        self.app_name = app_name.upper()
        self.base_url = os.getenv(f"{self.app_name}_URL")
        self.api_key = os.getenv(f"{self.app_name}_API_KEY")

    async def _get(self, endpoint, params=None):
        if not self.base_url or not self.api_key:
            return {"error": f"Missing config for {self.app_name}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v3/{endpoint}",
                    params={** (params or {}), "apiKey": self.api_key},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_queue(self):
        return await self._get("queue")

    async def get_system_status(self):
        return await self._get("system/status")

    async def search(self, term):
        if self.app_name == "RADARR":
            return await self._get("movie/lookup", params={"term": term})
        elif self.app_name == "SONARR":
            return await self._get("series/lookup", params={"term": term})
        return {"error": "Search not implemented for this app"}
