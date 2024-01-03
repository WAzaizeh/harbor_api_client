'''
Orchestrate Harbor API calls to list projects, repositories, and artifacts.
Then, delete artifact tags that are older than 30 days.
'''
import asyncio
from src.project_api_client import ProjectApiClient
from src.repository_api_client import RepositoryApiClient
from src.artifact_api_client import ArtifactApiClient
# from harbor_api_client import ProjectApiClient, RepositoryApiClient, ArtifactApiClient

async def main():

    # get list of projects
    projects = ProjectApiClient().list_projects()
    print(f'Found {len(projects)} projects')

    # get list of repositories for each project
    for project in projects:
        project_name = project["name"]
        repositories = RepositoryApiClient(project_name).list_repositories()
        print(f'Found {len(repositories)} repositories in project {project_name}')

        # get list of artifacts for each repository
        for repo in repositories:
            repo_name = repo["name"]
            artifact_client = ArtifactApiClient(project_name, repo_name)

            artifacts = artifact_client.list_artifacts()
            print(f'Found {len(artifacts)} artifacts in repository {repo_name}')

            # delete artifact tags that are older than 30 days
            print('Deleting old tags...')
            artifact_client.delete_old_tags(tags=30)

if __name__ == "__main__":  
    asyncio.run(main())