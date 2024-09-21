import os
from dotenv import load_dotenv
from db import search_similar_embeddings
from typing import List
import logging
from termcolor import colored
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up OpenAI API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://oai.helicone.ai/v1",
    default_headers={
        "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
    }
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_step(step: str, message: str):
    """
    Log a step in the process with a colorized output.
    """
    logging.info(f"{colored(step, 'blue', attrs=['bold'])}: {message}")

def get_embedding(text: str) -> List[float]:
    """
    Get the embedding for a given text using OpenAI's API.
    """
    log_step("EMBEDDING", f"Getting embedding for text: '{text[:50]}...'")
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    log_step("EMBEDDING", "Embedding generated successfully")
    return response.data[0].embedding  # Fixed: Correctly access the embedding data

def semantic_search(query: str, match_threshold: float = 0.5, match_count: int = 20):
    """
    Perform semantic search using the query and return similar README chunks.
    """
    log_step("SEARCH", f"Performing semantic search for query: '{query}'")
    query_embedding = get_embedding(query)
    results = search_similar_embeddings(query_embedding, match_threshold, match_count)
    log_step("SEARCH", f"Found {len(results)} similar chunks")
    for i, (name, full_name, content, similarity) in enumerate(results, 1):
        logging.info(colored(f"  Result {i}:", "cyan"))
        logging.info(f"    Repository: {full_name}")
        logging.info(f"    Content: {content[:100]}...")
        logging.info(f"    Similarity: {similarity:.4f}")
    return results

def generate_response(query: str, similar_chunks: List[tuple]) -> str:
    """
    Generate a well-formatted response for the user's starred repositories related to the query.
    """
    log_step("RESPONSE", "Generating response based on similar chunks")
    
    # Prepare the data for the prompt
    repo_data = []
    for name, full_name, content, similarity in similar_chunks:
        repo_data.append({
            "name": name,
            "full_name": full_name,
            "url": f"https://github.com/{full_name}",
            "content": content[:200],  # Limit content to 200 characters for brevity
            "similarity": similarity
        })
    
    # Sort repo_data by similarity in descending order
    repo_data.sort(key=lambda x: x['similarity'], reverse=True)
    
    prompt = f"""Query: {query}

Please provide a list of the user's starred GitHub repositories that are most relevant to the query. For each repository, include:

1. The repository name (as a clickable link)
2. A very brief description (1-2 sentences max)
3. The similarity score (as a percentage, rounded to one decimal place)

Use the following markdown format:

## Your Starred Repositories Related to "{query}"

1. **[Repository Name](link)** - Brief description.
   *Relevance: XX.X%*

2. **[Next Repository]**...

Include up to 5 most relevant repositories from the user's stars. If none are relevant, state that clearly.
At the end, add a note about the relevance scores."""

    log_step("RESPONSE", "Sending prompt to OpenAI")
    response = client.chat.completions.create(  # Fixed: Use chat.completions instead of ChatCompletion
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides concise, structured information about a user's starred GitHub repositories in markdown format."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.1,
    )
    generated_response = response.choices[0].message.content.strip()  # Fixed: Correctly access the message content
    log_step("RESPONSE", f"Generated response: '{generated_response}'")
    return generated_response

def retrieve_and_respond(query: str) -> str:
    """
    Main function to retrieve similar chunks and generate a response.
    """
    log_step("MAIN", f"Processing query: '{query}'")
    similar_chunks = semantic_search(query)
    if not similar_chunks:
        log_step("MAIN", "No similar chunks found")
        return "I couldn't find any relevant information to answer your query."
    
    response = generate_response(query, similar_chunks)
    log_step("MAIN", "Process completed successfully")
    return response