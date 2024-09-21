import os
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict
from dotenv import load_dotenv
import logging
# Load environment variables
load_dotenv()

# Get the database connection URL from the environment variable
DB_CONNECTION = os.getenv("DB_CONNECTION")

def get_db_connection():
    """
    Creates and returns a connection to the PostgreSQL database.
    """
    return psycopg2.connect(DB_CONNECTION)

def store_repository_and_embeddings(github_username: str, repo_info: Dict, chunks: List[str], embeddings: List[List[float]]):
    """
    Stores repository information, README chunks, and their embeddings in the database.
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

            # Insert README chunks
            chunk_data = [(repo_id, idx, chunk) for idx, chunk in enumerate(chunks)]
            execute_values(cur, """
                INSERT INTO readme_chunks (repository_id, chunk_index, content)
                VALUES %s
                RETURNING id
            """, chunk_data)
            chunk_ids = [row[0] for row in cur.fetchall()]

            # Insert embeddings
            embedding_data = [(repo_id, chunk_id, embedding) for chunk_id, embedding in zip(chunk_ids, embeddings)]
            execute_values(cur, """
                INSERT INTO embeddings (repository_id, chunk_id, embedding)
                VALUES %s
            """, embedding_data)

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
