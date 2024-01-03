import os
import httpx
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict
from  tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt

load_dotenv()

class BaseHarborApiClient:
    def __init__(self):
        self.base_url = os.environ.get("HARBOR_API_URL")
        self.username = os.environ.get("HARBOR_USERNAME") 
        self.password = os.environ.get("HARBOR_PASSWORD")

    @retry(retry=retry_if_exception_type(httpx.HTTPStatusError), wait=wait_fixed(2), stop=stop_after_attempt(3))
    async def request(self, method: str, endpoint: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        try:
            params = kwargs.pop("params", None)
            json = kwargs.pop("json", None)
            async with httpx.AsyncClient() as client:
                response = await client.request(method=method, 
                                                url=self.base_url + endpoint,
                                                params=params,
                                                json=json,
                                                auth=(self.username, self.password),
                                                **kwargs)
                response.raise_for_status()
                return response
        except httpx.NetworkError as exc:
            print(f"Network error: {exc}")
            raise exc
        except httpx.TimeoutException as exc:
            print(f"Timeout error: {exc}")
            raise exc 
        except Exception as exc:
            print(f"Unexpected error: {exc}")
            raise exc

    async def get(self, endpoint: str, **kwargs: Dict[str, Any]):
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Dict[str, Any], **kwargs: Dict[str, Any]): 
        return await self.request("POST", endpoint, data=data, **kwargs)

    async def put(self, endpoint: str, data: Dict[str, Any], **kwargs: Dict[str, Any]):
        return await self.request("PUT", endpoint, data=data, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Dict[str, Any]):
        return await self.request("DELETE", endpoint, **kwargs)