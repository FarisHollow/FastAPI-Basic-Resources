from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import openai 
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from fastapi.staticfiles import StaticFiles
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer

app = FastAPI()
app.mount("/view/chat", StaticFiles(directory="view/chat"), name="static")


load_dotenv()

openai.api_key = os.getenv("api_key")




if not openai.api_key:
    raise Exception("OpenAI API key not found. Please add it to your .env file.")

PERSIST_DIR = "./storage"

documents = SimpleDirectoryReader("data").load_data()
if not os.path.exists(PERSIST_DIR):

 index = VectorStoreIndex.from_documents(documents)
 index.storage_context.persist(persist_dir=PERSIST_DIR)

else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)



chat_store_path = "chat_store.json"

if os.path.exists(chat_store_path):
    chat_store = SimpleChatStore.from_persist_path(persist_path=chat_store_path)
else:
    chat_store = SimpleChatStore()


chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=3000,
    chat_store=chat_store,
    chat_store_key="user1",
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established.")
    
    try:
        while True:
            data = await websocket.receive_text() 
            print(f"User: {data}")
            await websocket.send_text(f"User: {data}")


            chat_engine = index.as_chat_engine(memory = chat_memory)
            response = str(chat_engine.chat(data))
            chat_store.persist(persist_path=chat_store_path)
            print(f"User: {response}")
            await websocket.send_text(f"Reply: {response}")
            

        

    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")




@app.get("/")
async def get():
    return FileResponse(os.path.join("view", "chat", "chat.html"))




