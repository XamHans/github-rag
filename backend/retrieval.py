import logging
from typing import List

from db import search_similar_embeddings
from dotenv import load_dotenv
from provider import AIProvider, ChatMessage, initialize_ai_provider
from termcolor import colored

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_step(step: str, message: str):
    """Log a step in the process with a colorized output."""
    logging.info(f"{colored(step, 'blue', attrs=['bold'])}: {message}")

async def semantic_search(query: str, ai_provider: AIProvider, match_threshold: float = 0.5, match_count: int = 20):
    """Perform semantic search using the query and return similar README chunks."""
    log_step("SEARCH", f"Performing semantic search for query: '{query}'")
    query_embedding = (await ai_provider.generate_embeddings([query]))[0]
    results = search_similar_embeddings(query_embedding, match_threshold, match_count)
    
    log_step("SEARCH", f"Found {len(results)} similar chunks")
    for i, (name, full_name, content, similarity) in enumerate(results, 1):
        logging.info(colored(f"  Result {i}:", "cyan"))
        logging.info(f"    Repository: {full_name}")
        logging.info(f"    Content: {content[:100]}...")
        logging.info(f"    Similarity: {similarity:.4f}")
    return results

async def generate_response(query: str, similar_chunks: List[tuple], ai_provider: AIProvider) -> str:
    """Generate a well-formatted response for the user's starred repositories related to the query."""
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

    log_step("RESPONSE", "Sending prompt to AI provider")
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant that provides concise, structured information about a user's starred GitHub repositories in markdown format."),
        ChatMessage(role="user", content=prompt)
    ]
    
    response = await ai_provider.chat_completion(
        messages=messages,
        max_tokens=1000,
        temperature=0.1
    )
    log_step("RESPONSE", f"Generated response: '{response.content}'")
    return response.content

async def retrieve_and_respond(query: str) -> str:
    """Main function to retrieve similar chunks and generate a response."""
    ai_provider = initialize_ai_provider()
    log_step("MAIN", f"Processing query: '{query}'")
    
    similar_chunks = await semantic_search(query, ai_provider)
    if not similar_chunks:
        log_step("MAIN", "No similar chunks found")
        return "I couldn't find any relevant information to answer your query."
    
    response = await generate_response(query, similar_chunks, ai_provider)
    log_step("MAIN", "Process completed successfully")
    return response