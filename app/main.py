import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.question_interpreter import answer_question


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mini AI Business Intelligence Assistant",
    description="Ask natural-language questions about sales data.",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
        description="A natural-language question about the sales data.",
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = answer_question(question)

        return {
            "question": question,
            "result": result,
        }

    except Exception:
        logger.exception("Failed to process question")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the question.",
        )