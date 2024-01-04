import re
import datetime as dt
from urllib.parse import quote
from typing import List, Dict, Any
from src.base_api_client import BaseHarborApiClient

class ArtifactApiClient(BaseHarborApiClient):

    @staticmethod
    def parse_repo_name(repo_name: str) -> str:
        if '/' in repo_name:
            repo_name = repo_name.split('/', maxsplit=1)[1]
            repo_name = repo_name.replace("/", "%252F")
        return repo_name

    async def list_artifacts(self, project_name: str, repository_name:str, page: int = 1, page_size: int = 100, **kwargs: Dict[str, Any]) -> List[Dict]:
        repository_name = self.parse_repo_name(repository_name)
        endpoint = f"/projects/{project_name}/repositories/{(repository_name)}/artifacts"
        return await self.paginated_get(endpoint, page=page, page_size=page_size, **kwargs)
    
    async def list_artifact_tags(self, project_name: str, repository_name:str, reference_name: str, page: int = 1, page_size: int = 100, **kwargs: Dict[str, Any]) -> List[Dict]:
        repository_name = self.parse_repo_name(repository_name)
        endpoint = f"/projects/{project_name}/repositories/{repository_name}/artifacts/{reference_name}/tags"
        return await self.paginated_get(endpoint, page=page, page_size=page_size, **kwargs)

    async def delete_ref(self, project_name: str, repository_name:str, reference_name: str, **kwargs: Dict[str, Any]) -> None:
        repository_name = self.parse_repo_name(repository_name)
        endpoint = f"/projects/{project_name}/repositories/{repository_name}/artifacts/{reference_name}"
        await self.delete(endpoint, **kwargs)