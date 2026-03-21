import asyncio
from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

PUBLIC_MEDIA_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp",
    "mp4", "avi", "mov", "webm", "mkv",
}


class MinioService:
    """Handle file storage with MinIO.

    The MinIO Python SDK is fully synchronous. All blocking calls are
    wrapped in asyncio.to_thread() so they don't stall the event loop.
    """

    def __init__(self, bucket: str | None = None):
        self.bucket = bucket or settings.MINIO_BUCKET_NAME
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def _is_public_media(self, object_name: str) -> bool:
        ext = object_name.rsplit(".", 1)[-1].lower() if "." in object_name else ""
        return ext in PUBLIC_MEDIA_EXTENSIONS
        
    def _ensure_bucket_sync(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def _upload_sync(self, object_name: str, contents: bytes, content_type: str) -> None:
        self._ensure_bucket_sync()
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=BytesIO(contents),
            length=len(contents),
            content_type=content_type,
        )

    def _file_exists_sync(self, object_name: str) -> bool:
        try:
            self.client.stat_object(bucket_name=self.bucket, object_name=object_name)
            return True
        except S3Error:
            return False

    def _delete_sync(self, object_name: str) -> None:
        self.client.remove_object(bucket_name=self.bucket, object_name=object_name)

    def _presigned_url_sync(self, object_name: str, expires_seconds: int) -> str:
        return self.client.presigned_get_object(
            bucket_name=self.bucket,
            object_name=object_name,
            expires=timedelta(seconds=expires_seconds),
        )

    async def upload_file(self, file, contents: bytes) -> str:
        """Upload pre-read bytes to MinIO. Returns object_name.

        BUG FIX: accepts pre-read bytes so the caller controls the single
        read and can use the same bytes for size reporting.
        """
        content_type = file.content_type or "application/octet-stream"
        object_name = file.filename or "upload"

        await asyncio.to_thread(self._upload_sync, object_name, contents, content_type)
        return object_name

    async def file_exists(self, object_name: str) -> bool:
        """Check if file exists (async, non-blocking)."""
        return await asyncio.to_thread(self._file_exists_sync, object_name)

    async def delete_file(self, object_name: str) -> None:
        """Delete file (async, non-blocking)."""
        await asyncio.to_thread(self._delete_sync, object_name)

    def get_file_url(self, object_name: str) -> str:
        """Return permanent URL for media, presigned URL for everything else."""
        if self._is_public_media(object_name):
            return self.get_permanent_url(object_name)
        return self.get_presigned_url(object_name)

    def get_permanent_url(self, object_name: str) -> str:
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket}/{object_name}"

    def get_presigned_url(self, object_name: str, expires: int = 86400) -> str:
        """Sync presigned URL — safe to call from sync context or via to_thread."""
        return self._presigned_url_sync(object_name, expires)
