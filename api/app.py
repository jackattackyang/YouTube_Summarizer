from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Any
from contextlib import asynccontextmanager
import uuid
from datetime import datetime, timedelta

from data.get_youtube_data import YouTubeDataFetcher
from data.preprocess import merge_chapter_transcript, get_prompt, get_video_info
from api.replicate_api import llama3_8b
from src.vectorstore import get_retriever
from src.chat import chat, get_chat_chain


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.chat_histories: Dict[str, List] = {}
        self.session_timestamps: Dict[str, datetime] = {}
        # Cleanup after 1 hour of inactivity
        self.cleanup_interval = timedelta(hours=1)

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {}
        self.chat_histories[session_id] = []
        self.session_timestamps[session_id] = datetime.now()
        return session_id

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id in self.sessions:
            self.session_timestamps[session_id] = datetime.now()
            return self.sessions.get(session_id, {})
        return {}

    def set_session(self, session_id: str, data: Dict[str, Any]):
        self.sessions[session_id] = data
        self.session_timestamps[session_id] = datetime.now()

    def get_chat_history(self, session_id: str) -> List:
        if session_id in self.chat_histories:
            self.session_timestamps[session_id] = datetime.now()
            return self.chat_histories.get(session_id, [])
        return []

    def set_chat_history(self, session_id: str, history: List):
        self.chat_histories[session_id] = history
        self.session_timestamps[session_id] = datetime.now()

    def cleanup_old_sessions(self):
        current_time = datetime.now()
        expired_sessions = [
            session_id
            for session_id, timestamp in self.session_timestamps.items()
            if (current_time - timestamp) > self.cleanup_interval
        ]
        for session_id in expired_sessions:
            self.sessions.pop(session_id, None)
            self.chat_histories.pop(session_id, None)
            self.session_timestamps.pop(session_id, None)


session_manager = SessionManager()


class YouTubeRequest(BaseModel):
    youtube_url: HttpUrl
    session_id: str = Field(..., description="Session ID for the current user session")


class QuestionRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the current user session")
    user_question: str


class SummaryResponse(BaseModel):
    response: str
    session_id: str
    youtube_url: str


class QAResponse(BaseModel):
    response: str
    youtube_url: str  # Include the YouTube URL for context


class VideoInfo(BaseModel):
    response: str
    youtube_url: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    youtube = YouTubeDataFetcher()
    app.state.youtube = youtube
    yield
    # Shutdown
    session_manager.cleanup_old_sessions()


app = FastAPI(
    title="YouTube Video Summarizer API",
    description="API for summarizing YouTube videos and answering questions",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_youtube_client():
    return app.state.youtube


@app.post("/create_session")
async def create_session():
    session_id = session_manager.create_session()
    return {"session_id": session_id}


@app.post("/summarize", response_model=SummaryResponse)
async def summarize(
    request: YouTubeRequest, youtube: YouTubeDataFetcher = Depends(get_youtube_client)
):
    try:
        meta_data = youtube.get_meta_data(str(request.youtube_url))
        chapter_transcript = merge_chapter_transcript(meta_data)
        prompt = get_prompt(meta_data, chapter_transcript)
        response = llama3_8b(prompt)

        retriever = get_retriever(meta_data, chapter_transcript)
        chat_chain = get_chat_chain(retriever)

        session_manager.set_session(
            request.session_id,
            {
                "meta_data": meta_data,
                "chapter_transcript": chapter_transcript,
                "retriever": retriever,
                "chat_chain": chat_chain,
                "youtube_url": str(request.youtube_url),
            },
        )

        return SummaryResponse(
            response=response,
            session_id=request.session_id,
            youtube_url=str(request.youtube_url),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/qa", response_model=QAResponse)
async def question_answer(request: QuestionRequest):
    session_data = session_manager.get_session(request.session_id)
    if not session_data or not session_data.get("chat_chain"):
        raise HTTPException(
            status_code=400,
            detail="Please summarize a YouTube video first for this session",
        )

    try:
        chat_chain = session_data["chat_chain"]
        chat_history = session_manager.get_chat_history(request.session_id)

        response, updated_history = chat(
            request.user_question, chat_chain, chat_history
        )

        session_manager.set_chat_history(request.session_id, updated_history)
        return QAResponse(
            response=response["answer"], youtube_url=session_data["youtube_url"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/video_info", response_model=VideoInfo)
async def video_info(
    request: YouTubeRequest, youtube: YouTubeDataFetcher = Depends(get_youtube_client)
):
    try:
        meta_data = youtube.get_meta_data(str(request.youtube_url))
        chapter_transcript = merge_chapter_transcript(meta_data)
        response = get_video_info(meta_data, chapter_transcript)

        return VideoInfo(response=response, youtube_url=str(request.youtube_url))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5001, reload=True)
