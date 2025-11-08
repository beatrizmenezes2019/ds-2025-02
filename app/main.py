from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import shutil
import uuid
import os
from .model import analyze_image
from .preprocessing import download_url_to_upload_file

app = FastAPI()

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post('/api/v1/analyze')
async def analyze(imagem_url: str = Form(...)):
    # salva arquivo temporariamente

    upload_file_object = download_url_to_upload_file(
        url=imagem_url
    )

    file_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{file_id}_{upload_file_object.filename}")
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file_object.file, buffer)

    # chama pipeline de análise (descrita no model.py)
    result = analyze_image(path)

    # resposta JSON
    return JSONResponse(content=result)

@app.get("/")
def root():
    return {"status": "ok"}