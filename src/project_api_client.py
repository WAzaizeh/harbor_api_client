import re
from typing import List, Dict, Any
from src.base_api_client import BaseHarborApiClient 

class ProjectApiClient(BaseHarborApiClient):

    def __init__(self):
        super().__init__()
        self.base_endpoint = "/projects"
        self.page = 1
        self.page_size = 10

    async def list_projects(self, **kwargs: Dict[str, Any]) -> List[Dict]:
        endpoint = self.base_endpoint
        params  = {"page": self.page, "page_size": self.page_size}
        projects = []

        while endpoint:
            response = await self.get(endpoint, params=params, **kwargs)

            # extend projects with current page data
            projects.extend(response.json())

            # check for next page in header Link
            links = response.headers.get("Link", None)
            if links:
                next_match = re.search(r'<(?P<url>.*?)>; rel="next"', links)
                endpoint = next_match.group("url") if next_match else None
            else:
                endpoint = None

        return projects