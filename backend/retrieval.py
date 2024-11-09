import logging
from typing import List, Tuple

from db import search_for_repos
from provider import AIProvider, ChatMessage, initialize_ai_provider
from termcolor import colored


def log_step(step: str, message: str):
    """Log a step in the process with a colorized output."""
    logging.info(f"{colored(step, 'blue', attrs=['bold'])}: {message}")

def format_repo_context(repos: List[Tuple]) -> str:
    """Format repository information into a structured context."""
    context = []
    for repo in repos:
        # The repo tuple contains (combined_text, similarity_score)
        combined_text, score = repo
        
        # Parse the combined text to extract information
        # Expected format: 'name: {name} url: {url} content: {content}'
        try:
            # Split only on the first occurrence of each keyword
            name_part = combined_text.split('name:', 1)[1].split('url:', 1)[0].strip()
            url_part = combined_text.split('url:', 1)[1].split('content:', 1)[0].strip()
            content_part = combined_text.split('content:', 1)[1].strip()
            
            # Format each repository's information
            context.append(f"""
Repository: {name_part}
URL: {url_part}
Relevance Score: {score:.2f}
Description: {content_part}
---""")
        except IndexError:
            # Handle malformed entries gracefully
            logging.warning(f"Malformed repository entry: {combined_text}")
            context.append(f"""
Repository Entry:
Raw Text: {combined_text}
Relevance Score: {score:.2f}
---""")
            
    return "\n".join(context)

async def generate_response(query: str) -> str:
    ai_provider = initialize_ai_provider()
    """Generate a well-formatted response for the user's query using RAG."""
    log_step("RESPONSE", "Generating response based on similar repositories")
    similar_repos = search_for_repos(query)
    
    # Format the repository context
    repo_context = format_repo_context(similar_repos)
    
    # Create a comprehensive RAG prompt
    system_prompt = """You are a technical assistant specializing in analyzing GitHub repositories. 
Your task is to:
1. Analyze the provided repository information
2. Understand the user's query and intent
3. Provide a comprehensive, well-structured response that connects the repositories to the user's needs
4. Be specific and reference actual features and capabilities from the repositories
5. Maintain technical accuracy while being clear and concise

Format your response in markdown and organize information logically."""

    user_prompt = f"""User Query: "{query}"

Available Repository Information:
{repo_context}

Please provide a response that:
1. Explains how these repositories specifically address the user's query
2. Highlights the most relevant features and capabilities from each repository
3. Provides a clear recommendation based on the repository details
4. Points out any limitations or considerations the user should be aware of

Focus on concrete details from the repository descriptions rather than making general statements."""

    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=user_prompt)
    ]
    
    response = await ai_provider.chat_completion(
        messages=messages,
        max_tokens=1500,  # Increased for more comprehensive responses
        temperature=0.1   # Keep low for factual responses
    )
    
    log_step("RESPONSE", "Generated structured response")
    return response.content