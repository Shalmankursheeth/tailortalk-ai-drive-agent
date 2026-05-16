from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import get_agent_response

app = FastAPI(title="TailorTalk Drive Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list = []


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {
        "message": "TailorTalk Backend Running"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    response = get_agent_response(req.message, req.history)
    return ChatResponse(response=response)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TailorTalk Drive Agent"
    }

import os
from agent import quick_drive_test
@app.get("/drive-test")
def drive_test():

    return quick_drive_test()

from agent import _get_drive_service
@app.get("/pdf-test")
def pdf_test():

    drive = _get_drive_service()

    result = drive.files().list(
        q="mimeType='application/pdf'",
        pageSize=20,
        fields="files(name,mimeType)"
    ).execute()

    return result

@app.get("/debug")
def debug():

    return {
        "groq_key_exists": bool(
            os.getenv("GROQ_API_KEY")
        ),

        "folder_id": os.getenv(
            "GOOGLE_DRIVE_FOLDER_ID"
        ),

        "service_account_file": os.getenv(
            "SERVICE_ACCOUNT_FILE",
            "service_account.json"
        )
    }