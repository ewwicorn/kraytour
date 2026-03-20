from io import BytesIO
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket_exists(client: Minio, bucket: str) -> None:
    """Создаёт бакет, если он ещё не существует."""
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def upload_file(
    data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
    bucket: str | None = None,
) -> str:
    """
    Загружает файл в MinIO и возвращает имя объекта.

    :param data: Байты файла.
    :param object_name: Имя объекта в бакете (например, "avatars/user_1.jpg").
    :param content_type: MIME-тип файла.
    :param bucket: Имя бакета (по умолчанию из настроек).
    :return: object_name загруженного объекта.
    """
    bucket = bucket or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    ensure_bucket_exists(client, bucket)

    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_name


def get_presigned_url(
    object_name: str,
    expires_seconds: int = 3600,
    bucket: str | None = None,
) -> str:
    """
    Генерирует временную ссылку для скачивания объекта.

    :param object_name: Имя объекта в бакете.
    :param expires_seconds: Время жизни ссылки в секундах (по умолчанию 1 час).
    :param bucket: Имя бакета.
    :return: Presigned URL.
    """
    from datetime import timedelta

    bucket = bucket or settings.MINIO_BUCKET_NAME
    client = get_minio_client()

    url = client.presigned_get_object(
        bucket_name=bucket,
        object_name=object_name,
        expires=timedelta(seconds=expires_seconds),
    )
    return url


def delete_file(object_name: str, bucket: str | None = None) -> None:
    """Удаляет объект из бакета."""
    bucket = bucket or settings.MINIO_BUCKET_NAME
    client = get_minio_client()
    client.remove_object(bucket_name=bucket, object_name=object_name)
