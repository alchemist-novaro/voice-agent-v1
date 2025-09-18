import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from livekit import api
from datetime import timedelta
import uuid

load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/connection-details")
async def get_token(identity: str, room: str = "voice-room"):
    at = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    at.with_grants(api.VideoGrants(room_join=True, room=f"room-{uuid.uuid4()}"))
    at.with_identity(identity)
    at.with_ttl(timedelta(4))
    token = at.to_jwt()
    return JSONResponse({
        "participantToken": token,
        "serverUrl": LIVEKIT_URL
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="localhost", port=8003, reload=False)
