from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading
import main
import uvicorn
from multiprocessing import Process



app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates folder
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/start-voice-assistant")
# async def start_voice_assistant():
#     threading.Thread(target=main.listen_and_respond, daemon=True).start()
#     return {"status": "Voice Assistant Started"}

@app.get("/start-voice-assistant")
async def start_voice_assistant():
    Process(target=main.listen_and_respond).start()
    return {"status": "Voice Assistant Started"}


if __name__ == "__main__":
    print("Server running at http://localhost:8000")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
