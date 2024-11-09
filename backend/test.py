import asyncio
import logging
import os
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from ingest import fetch_and_process_user_stars
from provider import AIProvider, ChatMessage, create_ai_provider
from retrieval import retrieve_and_respond
from termcolor import colored

# Configure logging with colors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_section(message: str):
    """Print a colored section header"""
    print("\n" + "=" * 80)
    print(colored(message, 'green', attrs=['bold']))
    print("=" * 80 + "\n")

async def status_callback(status: Dict):
    """Callback for processing status updates"""
    if "current_repo" in status:
        print(colored(
            f"Processing: {status['current_repo']} "
            f"({status['processed_count']}/{status['total_count']})",
            'cyan'
        ))
    elif "status" in status and status["status"] == "COMPLETE":
        print(colored("Processing completed!", 'green'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def env_setup():
    """Set up environment variables for testing"""
    load_dotenv()
    os.environ["AI_PROVIDER"] = "ollama"
    os.environ["OLLAMA_EMBED_MODEL"] = "nomic-embed-text"
    os.environ["OLLAMA_CHAT_MODEL"] = "llama3"
    return True

@pytest_asyncio.fixture(scope="session")
async def ai_provider(env_setup):
    """Create and yield an AI provider instance"""
    provider = create_ai_provider("ollama")
    return provider

@pytest.mark.asyncio
async def test_embeddings(ai_provider: AIProvider):
    """Test the embedding functionality"""
    log_section("Testing Embeddings")
    
    test_texts = [
        "This is a test text for embedding generation",
        "Another sample text to ensure multiple embeddings work",
    ]
    
    embeddings = await ai_provider.generate_embeddings(test_texts)
    
    assert len(embeddings) == len(test_texts)
    assert all(isinstance(emb, list) for emb in embeddings)
    assert all(isinstance(val, float) for emb in embeddings for val in emb)
    
    print(colored("✓ Embeddings generated successfully", 'green'))
    print(f"Number of embeddings: {len(embeddings)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")

@pytest.mark.asyncio
async def test_chat(ai_provider: AIProvider):
    """Test the chat functionality"""
    log_section("Testing Chat")
    
    test_prompt = "Explain what makes a good README file for a GitHub repository"
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant specializing in software development best practices."),
        ChatMessage(role="user", content=test_prompt)
    ]
    
    response = await ai_provider.chat_completion(messages)
    
    assert response.content and len(response.content) > 0
    assert isinstance(response.content, str)
    
    print(colored("✓ Chat completion generated successfully", 'green'))
    print("\nResponse:")
    print(colored("-" * 40, 'blue'))
    print(response.content)
    print(colored("-" * 40, 'blue'))

@pytest.mark.asyncio
async def test_ingest_flow(ai_provider: AIProvider):
    """Test the repository ingestion flow"""
    log_section("Testing Repository Ingestion")
    
    test_username = "simonw"  # Example: Simon Willison's account
    
    print(f"Starting ingestion for user: {test_username}")
    ingest_result = await fetch_and_process_user_stars(
        test_username,
        status_callback
    )
    
    assert ingest_result["status"] == "success"
    assert ingest_result["repos_processed"] > 0
    
    print(colored(
        f"✓ Successfully processed {ingest_result['repos_processed']} repositories",
        'green'
    ))

@pytest.mark.asyncio
async def test_search_and_chat(ai_provider: AIProvider):
    """Test the search and chat functionality"""
    log_section("Testing Search and Chat")
    
    test_queries = [
        "Python web frameworks",
        "Data visualization tools",
        "CLI development",
    ]

    for query in test_queries:
        print(colored(f"\nTesting query: {query}", 'yellow'))
        response = await retrieve_and_respond(query)
        
        assert response and len(response) > 0
        assert isinstance(response, str)
        
        print("\nResponse:")
        print(colored("-" * 40, 'blue'))
        print(response)
        print(colored("-" * 40, 'blue'))
        
        print(colored("✓ Response received and validated", 'green'))
        
        # Add a small delay between queries
        await asyncio.sleep(2)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])