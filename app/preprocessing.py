import requests
import io
from fastapi import UploadFile, HTTPException
from starlette.datastructures import UploadFile as StarletteUploadFile

def download_url_to_upload_file(url: str) -> UploadFile:
    filename = url.split("/")[-1]  

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Mantém o arquivo na memória
        file_like_object = io.BytesIO(response.content)

        # Starlette UploadFile aceita apenas `file` e `filename`
        upload_file = StarletteUploadFile(file=file_like_object, filename=filename)

        return upload_file

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Erro ao baixar a imagem: {e}")
