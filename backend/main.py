from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    messages: str   

@app.post("/ask")
async def ask_ai():

    return {"response": "This is a response from the AI therapist."}