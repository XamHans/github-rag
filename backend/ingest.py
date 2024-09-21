import os
import requests
import base64
from typing import List, Dict, Callable
import openai
from db import store_repository_and_embeddings
import logging
from dotenv import load_dotenv
import asyncio
from openai import OpenAI

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Assume OpenAI API key is set in environment variables
# openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://oai.helicone.ai/v1",
    default_headers={
        "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
    }
)
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

                repo_info = {
                    "name": repo["name"],
                    "full_name": repo_name,
                    "description": repo["description"],
                    "url": repo["html_url"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                }

                readme_content = fetch_readme(repo_name)

                if readme_content:
                    logging.info(f"README found for {repo_name}. Processing...")
                    chunks = create_chunks(readme_content)
                    embeddings = generate_embeddings(chunks)
                    store_repository_and_embeddings(github_username, repo_info, chunks, embeddings)
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

    except requests.RequestException as e:
        logging.error(f"Error fetching starred repositories: {str(e)}")
        raise Exception(f"Error fetching starred repositories: {str(e)}")

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

def create_chunks(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Splits the text into overlapping chunks.
    """
    logging.info(f"Creating chunks with size {chunk_size} and overlap {overlap}")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    logging.info(f"Created {len(chunks)} chunks")
    return chunks

def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of text chunks using OpenAI's API.
    """
    logging.info(f"Generating embeddings for {len(chunks)} chunks")
    try:
        response = client.embeddings.create(
            input=chunks,
            model="text-embedding-ada-002",
            extra_headers={
                "Helicone-Cache-Enabled": "true"
            }
        )
        embeddings = [data.embedding for data in response.data]
        logging.info(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings
    except Exception as e:
        logging.error(f"Error generating embeddings: {str(e)}")
        raise Exception(f"Error generating embeddings: {str(e)}")