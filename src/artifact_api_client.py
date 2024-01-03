import re
import datetime as dt
from typing import List, Dict, Any
from src.base_api_client import BaseHarborApiClient 

class ArtifactApiClient(BaseHarborApiClient):

    def __init__(self, project_name: str, repository_name: str):
        super().__init__()
        self.project_name = project_name
        self.repository_name = repository_name
        self.base_endpoint = f"/projects/{self.project_name}/repositories/{self.repository_name}/artifacts"
        self.page = 1
        self.page_size = 10

    async def list_artifacts(self,  **kwargs: Dict[str, Any]) -> List[Dict]:
        endpoint = self.base_endpoint
        params  = {"page": self.page, "page_size": self.page_size}
        artifacts = []

        while endpoint:
            response = await self.get(endpoint, params=params, **kwargs)

            # extend projects with current page data
            artifacts.extend(response.json())

            # check for next page in header Link
            links = response.headers.get("Link", None)
            if links:
                next_match = re.search(r'<(?P<url>.*?)>; rel="next"', links)
                endpoint = next_match.group("url") if next_match else None
            else:
                endpoint = None

        return artifacts
    
    async def delete_old_tags(self,  days: int = 30) -> None:
        
        artifacts = await self.list_artifacts(self.project_name, self.repository_name)
        
        # cutoff date 
        cutoff = dt.datetime.utcnow() - dt.timedelta(days=days)
        
        for tag in artifacts['tags']:
            if tag["push_time"] < cutoff:  
                ref = tag["name"]
                endpoint = self.base_endpoint + f"/{ref}"
                
                await self.delete(endpoint)