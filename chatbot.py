from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import openai 
import os
from llama_index.core import SimpleKeywordTableIndex
from llama_index.llms.openai import OpenAI

app = FastAPI()

load_dotenv()

openai.api_key = os.getenv("api_key")


if not openai.api_key:
    raise Exception("OpenAI API key not found. Please add it to your .env file.")


class ChatRequest (BaseModel):
    text: str

class chatResponse (BaseModel):
    reply: str


@app.post("/chat", response_model=chatResponse)
async def apiCall(req: ChatRequest):

 try:

    

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= [
            { "role": "system", "content": "You're a great problem solver about medicine"},
            { "role": "user", "content": req.text},
        ],
    )      
    reply = response.choices[0].message.content
    return {"reply": reply}
 
 except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
