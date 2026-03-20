import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.minio_service import delete_file, get_presigned_url, upload_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", summary="Загрузить файл в MinIO")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    object_name = f"uploads/{uuid.uuid4()}.{ext}"

    try:
        name = upload_file(
            data=data,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {e}")

    return {"object_name": name}


@router.get("/url/{object_name:path}", summary="Получить временную ссылку")
async def presigned_url(object_name: str, expires: int = 3600):
    try:
        url = get_presigned_url(object_name=object_name, expires_seconds=expires)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Объект не найден: {e}")
    return {"url": url}


@router.delete("/{object_name:path}", summary="Удалить файл")
async def remove_file(object_name: str):
    try:
        delete_file(object_name=object_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {e}")
    return {"detail": "Файл удалён"}
