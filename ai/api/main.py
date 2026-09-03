from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai.ticket_ai.ticket_generator import generate_ticket


app = FastAPI(
    title="Complaint Management AI Service",
    version="1.0.0",
)


class ClassifyRequest(BaseModel):
    complaint_text: str


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Complaint Management AI Service",
    }


@app.post("/classify")
def classify(request: ClassifyRequest):
    complaint_text = request.complaint_text.strip()

    if len(complaint_text) < 5:
        raise HTTPException(
            status_code=400,
            detail="Complaint text must be at least 5 characters.",
        )

    ticket = generate_ticket(complaint_text)

    return {
        "category": ticket["category"],
        "priority": ticket["priority"],
        "complexity": ticket["complexity"],
        "recommended_team": ticket["recommended_team"],
        "confidence": None,
        "ticket": ticket,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if len(message) < 1:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    ticket = generate_ticket(message)

    return {
        "reply": (
            f"I analyzed your complaint. "
            f"Category: {ticket['category']}, "
            f"Priority: {ticket['priority']}, "
            f"Complexity: {ticket['complexity']}, "
            f"Recommended Team: {ticket['recommended_team']}."
        ),
        "intent": "complaint",
        "resolved": False,
        "extracted_complaint": message,
        "ticket": ticket,
        "session_id": request.session_id,
    }