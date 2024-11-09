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
                INSERT INTO repositories (github_username, name, full_name, description, url, language, stars)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (github_username, repo_info['name'], repo_info['full_name'], repo_info['description'],
                  repo_info['url'], repo_info['language'], repo_info['stars']))
            repo_id = cur.fetchone()[0]
 
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error storing repository and embeddings: {str(e)}")
    finally:
        conn.close()

def search_similar_embeddings(query_embedding: List[float], match_threshold: float = 0.8, match_count: int = 5):
    """
    Searches for similar embeddings in the database.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            logging.info(f"Executing search query with threshold {match_threshold} and count {match_count}")
            cur.execute("""
                SELECT r.name, r.full_name, rc.content, s.similarity
                FROM search_similar_embeddings(%s::vector, %s, %s) s
                JOIN embeddings e ON s.repository_id = e.repository_id AND s.chunk_id = e.chunk_id
                JOIN repositories r ON e.repository_id = r.id
                JOIN readme_chunks rc ON e.chunk_id = rc.id
                ORDER BY s.similarity DESC
            """, (query_embedding, match_threshold, match_count))
            results = cur.fetchall()
            logging.info(f"Search query returned {len(results)} results")
            return results
    finally:
        conn.close()
