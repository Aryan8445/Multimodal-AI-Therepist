from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class Query(BaseModel):
    message: str


@app.post("/ask")
async def ask(query: Query):
    # response = ai_agent(query)
    response = "This is a response from the AI therapist."
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


