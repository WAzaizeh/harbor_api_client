'''
Orchestrate Harbor API calls to list projects, repositories, and artifacts.
Then, delete artifact tags that are older than 30 days.
'''

import os
import asyncio
import datetime as dt
from dotenv import load_dotenv
from src.project_api_client import ProjectApiClient
from src.repository_api_client import RepositoryApiClient
from src.artifact_api_client import ArtifactApiClient
# from harbor_api_client import ProjectApiClient, RepositoryApiClient, ArtifactApiClient

async def main():
    # load environment variables
    load_dotenv()
    base_url = os.environ.get("HARBOR_API_URL", "https://demo.goharbor.io/api/v2.0")
    harbor_username = os.environ.get("HARBOR_USERNAME")
    harbor_password = os.environ.get("HARBOR_PASSWORD")

    # validate necessary auth variables are set
    if harbor_username is None or harbor_password is None:
        raise ValueError("Make sure to set HARBOR_USERNAME and HARBOR_PASSWORD in your .env file")
    if base_url is None:
            raise ValueError("Make sure to set HARBOR_API_URL in your .env file")

    # get list of projects
    project_client = ProjectApiClient(base_url=base_url,
                                      harbor_username=harbor_username,
                                      harbor_password=harbor_password)
    projects = await project_client.list_projects()
    print(f'Found {len(projects)} projects')

    # get list of repositories for each project
    for project in projects:
        project_name = project["name"]
        repo_client = RepositoryApiClient(base_url=base_url,
                                        harbor_username=harbor_username,
                                        harbor_password=harbor_password)
        repositories = await repo_client.list_repositories(project_name)
        print(f'Found {len(repositories)} repositories in project {project_name}')

        # get list of artifacts for each repository
        for repo in repositories:
            repo_name = repo["name"]
            artifact_client = ArtifactApiClient(base_url=base_url,
                                                harbor_username=harbor_username,
                                                harbor_password=harbor_password)

            artifacts = await artifact_client.list_artifacts(project_name, repo_name)
            print(f'Found {len(artifacts)} artifacts in {repo_name}')

            for artifact in artifacts:
                artifact_tages = await artifact_client.list_artifact_tags(project_name, repo_name, artifact["digest"])

                # delete artifact older than 30 days
                for tag in artifact_tages:
                    if dt.datetime.strptime(tag["push_time"], "%Y-%m-%dT%H:%M:%S.%fZ") < dt.datetime.utcnow() - dt.timedelta(days=30):
                        print(f'Deleting tag {tag["name"]}')
                        await artifact_client.delete_ref(project_name, repo_name, tag["name"])

if __name__ == "__main__":  
    asyncio.run(main())