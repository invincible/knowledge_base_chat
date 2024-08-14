from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from .database import SessionLocal, engine
from . import models
from .chatbot_logic import process_user_input

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserInput(BaseModel):
    message: str
    context: dict = {}

class ChatResponse(BaseModel):
    response: str
    buttons: List[str] = []
    spoiler: Optional[str] = None
    table: Optional[str] = None
    context: dict

@app.post("/chat", response_model=ChatResponse)
def chat(user_input: UserInput, db: Session = Depends(get_db)):
    response, new_context = process_user_input(db, user_input.message, user_input.context)
    if isinstance(response, tuple):
        return ChatResponse(
            response=response[0],
            buttons=response[1],
            spoiler=response[2],
            table=response[3],
            context=new_context
        )
    else:
        return ChatResponse(response=response, context=new_context)

# Здесь можно добавить дополнительные эндпоинты для управления деревьями решений