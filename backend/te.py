import asyncio
from typing import Dict

from ingest import fetch_and_process_user_stars


async def status_callback(status: Dict) -> None:
    """
    Callback function to handle status updates from the ingestion process
    """
    if "current_repo" in status:
        print(f"Processing: {status['current_repo']} ({status['processed_count']}/{status['total_count']})")
    elif "status" in status and status["status"] == "COMPLETE":
        print("Processing complete!")

async def test_github_stars_ingestion():
    """
    Test function to run the GitHub stars ingestion for a specific user
    """
    github_username = "xamhans"
    
    try:
        print(f"Starting ingestion for user: {github_username}")
        result = await fetch_and_process_user_stars(github_username, status_callback)
        
        print("\nIngestion completed successfully!")
        print(f"Total repositories processed: {result['repos_processed']}")
        print(f"Status: {result['status']}")
        
    except Exception as e:
        print(f"Error during ingestion: {str(e)}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_github_stars_ingestion())