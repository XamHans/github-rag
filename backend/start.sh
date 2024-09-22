#!/bin/bash

# Start FastAPI server
poetry run uvicorn server:app --host 0.0.0.0 --port $PORT &

# Start LiteLLM server
poetry run litellm --model gpt-3.5-turbo --port 8000 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?