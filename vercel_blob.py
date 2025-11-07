# vercel_blob.py
import os
import httpx
import base64
import asyncio

VERCEL_BLOB_URL = "https://blob.vercel-storage.com"
VERCEL_TOKEN = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")


async def put(path: str, data: bytes, content_type: str, access: str = "public"):
    """
    Uploads a file (bytes or string) to Vercel Blob storage.
    Returns the public URL of the uploaded file.
    """
    if not VERCEL_TOKEN:
        raise EnvironmentError("Missing VERCEL_BLOB_READ_WRITE_TOKEN environment variable")

    # Ensure data is bytes
    if isinstance(data, str):
        data = data.encode("utf-8")

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "x-vercel-blob-content-type": content_type,
        "x-vercel-blob-access": access,
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{VERCEL_BLOB_URL}/{path}", content=data, headers=headers)

    if response.status_code not in (200, 201):
        raise Exception(f"Blob upload failed: {response.status_code} - {response.text}")

    blob_data = response.json()
    return blob_data.get("url")
