import logging
import os
from typing import Dict, List

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()

# Get the database connection URL from the environment variable
DB_CONNECTION = os.getenv("DB_CONNECTION")

def get_db_connection():
    """
    Creates and returns a connection to the PostgreSQL database.
    """
    return psycopg2.connect(DB_CONNECTION)

def store_repository(github_username: str, repo_info: Dict):
    """
    Stores repository information, README chunks, and their embeddings in the vector database.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Insert repository information
            cur.execute("""
                INSERT INTO repositories (github_username, name, full_name, readme, description, url, language, stars)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (github_username, repo_info['name'], repo_info['full_name'], repo_info['readme'], repo_info['description'],
                  repo_info['url'], repo_info['language'], repo_info['stars']))
            repo_id = cur.fetchone()[0]
 
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error storing repository and embeddings: {str(e)}")
    finally:
        conn.close()

def search_for_repos(query: str, limit: int = 5):
    """
       -- Perform similarity search to find relevant blog posts

    Args:
        query_embedding: The embedding vector to search with
        match_threshold: Threshold for similarity matching
        limit: Maximum number of results to return
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            logging.info("Executing semantic search query")
            cur.execute("""
                SELECT 
                    chunk,
                    embedding <=> ai.openai_embed('text-embedding-3-small', %s) as distance
                FROM "public"."repositories_embedding_store"
                ORDER BY distance
                LIMIT %s
            """, (query, limit))
            results = cur.fetchall()
            logging.info(f"Search query returned {len(results)} results")
            return results
    finally:
        conn.close()
