import os
import httpx
import asyncio
import warnings
from pathlib import Path
from typing import Any, Dict, Tuple
from  tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt


class BaseHarborApiClient:

    def __init__(self, base_url: str, harbor_username: str, harbor_password: str, **kwargs: Dict[str, Any]):
        self.base_url = base_url
        self.harbor_username = harbor_username
        self.harbor_password = harbor_password

    @retry(retry=retry_if_exception_type(httpx.HTTPStatusError), wait=wait_fixed(2), stop=stop_after_attempt(3))
    async def request(self, method: str, endpoint: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        try:
            params = kwargs.pop("params", None)
            json = kwargs.pop("json", None)
            async with httpx.AsyncClient() as client:
                response = await client.request(method=method, 
                                                url=self.base_url+ endpoint,
                                                auth=(self.harbor_username, self.harbor_password),
                                                params=params,
                                                json=json,
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
    
    async def paginated_get(self, endpoint: str, page: int = 1, page_size: int = 100, **kwargs: Dict[str, Any]):
        params = {"page": page, "page_size": page_size}

        result = []
        while params['page']:
            response = await self.get(endpoint, params=params, **kwargs)
            response_data  = response.json()
            
            if response_data is None:
                warnings.warn(f"No data returned for endpoint {endpoint} with the following parameters {', '.join([str(val) for val in params.items()])}", Warning)
            else:
                result.extend(response_data)
            params['page'] = params['page'] + 1 if response.links.get('next', {}).get('rel') == 'next' else None

        return result