import asyncio
import base64
import logging
import os
from typing import Callable, Dict, List

import requests
from db import store_repository
from dotenv import load_dotenv
from provider import initialize_ai_provider

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def fetch_and_process_user_stars(github_username: str, send_status: Callable[[Dict], None]) -> Dict:
    """
    Fetches and processes all starred repositories for a given GitHub user.
    """
    logging.info(f"Starting to fetch and process starred repositories for user: {github_username}")
    
    try:
        processed_repos = []
        page = 1
        per_page = 100
        total_repos = 0

        # First, get the total number of starred repositories
        api_url = f"https://api.github.com/users/{github_username}/starred?per_page=1"
        response = requests.get(api_url)
        response.raise_for_status()
        total_repos = int(response.headers.get('Link').split(',')[1].split('&page=')[1].split('>')[0])

        while True:
            api_url = f"https://api.github.com/users/{github_username}/starred?page={page}&per_page={per_page}"
            logging.info(f"Fetching starred repositories from: {api_url}")
            response = requests.get(api_url)
            response.raise_for_status()

            starred_repos = response.json()
            if not starred_repos:
                break

            logging.info(f"Processing {len(starred_repos)} repositories on page {page}")

            for index, repo in enumerate(starred_repos, 1):
                repo_name = repo["full_name"]
                logging.info(f"Processing repository {index + (page-1)*per_page}: {repo_name}")

                await send_status({
                    "current_repo": repo_name,
                    "processed_count": len(processed_repos),
                    "total_count": total_repos
                })

                readme_content = fetch_readme(repo_name)


                repo_info = {
                    "name": repo["name"],
                    "full_name": repo_name,
                    "description": repo["description"],
                    "readme": readme_content,
                    "url": repo["html_url"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                }
                logging.info(f"Processing: {repo_info}")


                if readme_content:
                    store_repository(github_username, repo_info)
                    logging.info(f"Processed and stored info for {repo_name}")
                else:
                    logging.warning(f"No README found for {repo_name}")

                processed_repos.append(repo_info)

            if 'next' not in response.links:
                break

            page += 1

        logging.info(f"Finished processing all repositories for user: {github_username}")
        await send_status({"status": "COMPLETE"})
        return {
            "github_username": github_username,
            "repos_processed": len(processed_repos),
            "repositories": processed_repos,
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Error processing repositories: {str(e)}")
        raise

def fetch_readme(repo_full_name: str) -> str:
    """
    Fetches the README content for a given repository.
    """
    logging.info(f"Fetching README for repository: {repo_full_name}")
    try:
        readme_url = f"https://api.github.com/repos/{repo_full_name}/readme"
        response = requests.get(readme_url)
        if response.status_code == 200:
            content = response.json()["content"]
            logging.info(f"Successfully fetched README for {repo_full_name}")
            return base64.b64decode(content).decode('utf-8')
        logging.warning(f"README not found for {repo_full_name}")
        return None
    except requests.RequestException as e:
        logging.error(f"Error fetching README for {repo_full_name}: {str(e)}")
        return None



