import os
from typing import List, Dict, Any
from src.base_api_client import BaseHarborApiClient 

class ProjectApiClient(BaseHarborApiClient):

    async def list_projects(self, page: int = 1, page_size: int = 100, **kwargs: Dict[str, Any]) -> List[Dict]:
        endpoint = "/projects"
        return await self.paginated_get(endpoint, page=page, page_size=page_size, **kwargs)