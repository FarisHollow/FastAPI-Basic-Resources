from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import openai 
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

app = FastAPI()

load_dotenv()

openai.api_key = os.getenv("api_key")


if not openai.api_key:
    raise Exception("OpenAI API key not found. Please add it to your .env file.")


documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

class ChatRequest (BaseModel):
    text: str

class chatResponse (BaseModel):
    reply: str


@app.post("/chat", response_model=chatResponse)
async def apiCall(req: ChatRequest):

 try:

    query_engine = index.as_query_engine()
    response = str(query_engine.query(req.text))

    return JSONResponse(content={"reply": response})
 
 except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
