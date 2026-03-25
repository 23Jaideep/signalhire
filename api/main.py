from fastapi import FastAPI
from core.storage.db import load_session, load_events, load_sessions

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/session/{session_id}")
def get_session(session_id: str):
    session = load_session(session_id)
    events = load_events(session_id)

    return {
        "summary": session["summary"],
        "events": events
    }

@app.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: str):
    sessions = load_sessions(candidate_id)

    return {
        "sessions": sessions
    }