from contextlib import asynccontextmanager
from fastapi import FastAPI
from main import sendMessage, getMessages
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the openAI client
    yield
    # Clean up the ML models and release the resources

app = FastAPI(lifespan=lifespan)

@app.get("/chat")
async def chat(thread_id: str = None):
    if thread_id is not None:
        res = await getMessages(thread_id)
    else:
        # start new chat
        res = await sendMessage("", None)

    return json.dumps(res)

@app.get("/sendMessage")
async def start_chat(query: str = "Hello.", thread_id: str = None):
    res = await sendMessage(query, thread_id)
    return json.dumps(res)