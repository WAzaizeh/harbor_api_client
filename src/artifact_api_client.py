import re
import datetime as dt
from urllib.parse import quote
from typing import List, Dict, Any
from src.base_api_client import BaseHarborApiClient

def parse_repo_name(repo_name: str) -> str:
    if '/' in repo_name:
        repo_name = quote(repo_name, safe='')
        repo_name = quote(repo_name, safe='')
    return repo_name

class ArtifactApiClient(BaseHarborApiClient):

    def __init__(self, project_name: str, repository_name: str):
        super().__init__()
        self.project_name = project_name
        self.repository_name = parse_repo_name(repository_name)
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

    async def delete_ref(self, reference_name: str, **kwargs: Dict[str, Any]) -> None:
        endpoint = self.base_endpoint + f"/{reference_name}"
        await self.delete(endpoint, **kwargs)