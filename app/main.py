from fastapi import FastAPI, UploadFile, Form, HTTPException, Request, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.embeddings import scrape_url_content, extract_pdf_content, get_embedding
import uuid

app = FastAPI()

# In-memory storage for content
storage = {}

templates = Jinja2Templates(directory="templates")

class URLRequest(BaseModel):
    url: str
 

class ChatRequest(BaseModel):
    chat_id: str
    question: str


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process_url")
async def process_url(request: Request, url: str = Form(...)):
    try:
        content = scrape_url_content(url)
        chat_id = str(uuid.uuid4())
        storage[chat_id] = content
        return templates.TemplateResponse(
            "result.html", 
            {"request": request, "chat_id": chat_id, "message": "URL content processed and stored successfully."}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/process_pdf")
async def process_pdf(request: Request, file: UploadFile = File(...)):
    try:
        print(f"Uploaded file: {file.filename}, Content type: {file.content_type}")

        pdf_content = await file.read()
        # Debug: Check file content size
        print(f"File size: {len(pdf_content)} bytes")
        text = extract_pdf_content(pdf_content)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract content from PDF.")
        chat_id = str(uuid.uuid4())
        storage[chat_id] = text
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "chat_id": chat_id, "message": "PDF content processed and stored successfully."}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/chat")
async def chat(request: Request, chat_id: str = Form(...), question: str = Form(...)):
    try:
        content = storage.get(chat_id)
        if not content:
            raise HTTPException(status_code=404, detail="Chat ID not found.")
        
        content_embedding = get_embedding(content)
        response = content_embedding.similarity_search(question)
        return templates.TemplateResponse(
            "chat_result.html",
            {"request": request, "response": response[0], "chat_id": chat_id, "question": question}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
