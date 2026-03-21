from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.minio_service import MinioService
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp",
    "pdf", "doc", "docx", "txt",
    "mp4", "avi", "mov",
}

ALLOWED_MIMETYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "video/mp4", "video/x-msvideo", "video/quicktime",
}


async def validate_file(file: UploadFile) -> bytes:
    """Read file once, validate size/type/extension, return contents.

    Returns raw bytes so the caller can pass them to the storage layer
    without reading the file stream a second time.
    """
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    if file.content_type not in ALLOWED_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(sorted(ALLOWED_MIMETYPES))}",
        )

    if file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension .{ext} not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

    return contents


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload file to MinIO storage."""
    contents = await validate_file(file)

    try:
        minio_service = MinioService()
        object_name = await minio_service.upload_file(file, contents)
        return {"object_name": object_name, "size": len(contents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/url/{object_name:path}")
async def get_file_url(
    object_name: str,
    current_user: User = Depends(get_current_user),
):
    """Get file URL (permanent for photos/videos, presigned for other files)."""
    try:
        minio_service = MinioService()
        if not await minio_service.file_exists(object_name):
            raise HTTPException(status_code=404, detail="File not found")
        url = minio_service.get_file_url(object_name)
        return {"url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{object_name:path}")
async def delete_file(
    object_name: str,
    current_user: User = Depends(get_current_user),
):
    """Delete file from MinIO storage."""
    try:
        minio_service = MinioService()
        await minio_service.delete_file(object_name)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
