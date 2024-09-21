from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from retrieval import retrieve_and_respond
from ingest import fetch_and_process_user_stars
import json
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for chat history and active WebSocket connections
chat_history = []
active_connections = set()

class GithubUsername(BaseModel):
    github_username: str

class ChatMessage(BaseModel):
    message: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if 'github_username' in data:
                await process_github_stars(data['github_username'], websocket)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def process_github_stars(github_username: str, websocket: WebSocket):
    try:
        async def send_status(status):
            await websocket.send_json({"status": status})

        await send_status({"status": "FETCHING_REPOS"})
        result = await fetch_and_process_user_stars(github_username, send_status)
        await websocket.send_json(result)
    except Exception as e:
        logging.error(f"Error processing user stars: {str(e)}")
        await websocket.send_json({"error": str(e)})

@app.post("/ingest")
async def ingest_stars(github_username: GithubUsername):
    logging.info("Received request to /ingest endpoint")
    if not github_username.github_username:
        logging.warning("No GitHub username provided in the request")
        raise HTTPException(status_code=400, detail="No GitHub username provided")
    
    logging.info(f"Processing stars for GitHub user: {github_username.github_username}")
    
    try:
        logging.info("Calling fetch_and_process_user_stars function")
        result = await fetch_and_process_user_stars(github_username.github_username, lambda x: None)
        logging.info("Successfully processed user stars")
        return JSONResponse(content={"message": "GitHub user stars processed successfully", "result": result}, status_code=201)
    except Exception as e:
        logging.error(f"Error processing user stars: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    logging.info("Received request to /chat endpoint")
    if not chat_message.message:
        logging.warning("No message provided in the chat request")
        raise HTTPException(status_code=400, detail="No message provided")
    
    user_message = chat_message.message
    logging.info(f"Received user message: {user_message}")
    
    try:
        response = retrieve_and_respond(user_message)
        logging.info(f"Generated response: {response}")
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        response = "I'm sorry, but I encountered an error while processing your request."
    
    chat_history.append({"user": user_message, "assistant": response})
    logging.info("Updated chat history")
    
    return {
        "response": response,
        "chat_history": chat_history
    }

@app.get("/health")
async def health_check():
    logging.info("Received request to /health endpoint")
    return {"status": "healthy"}

if __name__ == '__main__':
    import uvicorn
    logging.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)