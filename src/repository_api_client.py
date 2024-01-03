import re
from typing import List, Dict, Any
from src.base_api_client import BaseHarborApiClient 

class RepositoryApiClient(BaseHarborApiClient):

    async def list_repositories(self, project_name: str, page: int = 1, page_size: int = 100, **kwargs: Dict[str, Any]) -> List[Dict]:
        endpoint = f"/projects/{project_name}/repositories"
        return await self.paginated_get(endpoint=endpoint, page=page, page_size=page_size, **kwargs)