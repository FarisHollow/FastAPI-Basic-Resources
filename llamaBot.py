from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import openai 
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from fastapi.staticfiles import StaticFiles
import logging

app = FastAPI()
app.mount("/view/chat", StaticFiles(directory="view/chat"), name="static")

load_dotenv()

openai.api_key = os.getenv("api_key")


if not openai.api_key:
    raise Exception("OpenAI API key not found. Please add it to your .env file.")

PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
 documents = SimpleDirectoryReader("data").load_data()
 index = VectorStoreIndex.from_documents(documents)
 index.storage_context.persist(persist_dir=PERSIST_DIR)

else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

class ChatRequest (BaseModel):
    text: str

class chatResponse (BaseModel):
    reply: str


# ws =  WebSocket("ws://localhost:8000/ws")




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established.")
    
    try:
      
            data = await websocket.receive_text() 
            print(f"User: {data}")
            await websocket.send_text(f"User: {data}")


            query_engine = index.as_query_engine()
            response = str(query_engine.query(data))
            await websocket.send_text(f"Reply: {response}")
            print(f"Reply: {response}")

    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")




@app.get("/")
async def get():
    return FileResponse(os.path.join("view", "chat", "chat.html"))




# @app.post("/chat", response_model=chatResponse)
# async def apiCall(req: ChatRequest):

#  try:
  
#     query_engine = index.as_query_engine()
#     response = str(query_engine.query(req.text))

#     return JSONResponse(content={"reply": response})
 
#  except Exception as e:
        
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")




# while True:
#     text_input = input("User: ")
#     if text_input == "exit":
#         break
#     query_engine = index.as_query_engine()

#     response = str(query_engine.query(text_input))

#     def on_open(ws):
#         ws.send(response)

    
#     print(f"Agent: {response}")

