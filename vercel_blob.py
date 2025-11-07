import os
import httpx
import asyncio

VERCEL_BLOB_URL = "https://fbgruph4dru1oifl.public.blob.vercel-storage.com"
VERCEL_TOKEN = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")

async def put(path: str, data, content_type: str, access: str = "public"):
    """
    Uploads file data to Vercel Blob correctly as raw binary.
    Returns a working download URL.
    """

    if not VERCEL_TOKEN:
        raise EnvironmentError("Missing VERCEL_BLOB_READ_WRITE_TOKEN environment variable")

    # Convert data properly
    if isinstance(data, str):
        data = data.encode("utf-8")  # for CSV/text
    elif not isinstance(data, (bytes, bytearray)):
        raise TypeError("Data must be str or bytes")

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "x-vercel-blob-content-type": content_type,
        "x-vercel-blob-access": access,
    }

    params = {"slug": path}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{VERCEL_BLOB_URL}",
            params=params,
            content=data,
            headers=headers,
            timeout=60.0
        )

    if response.status_code not in (200, 201):
        raise Exception(f"Blob upload failed: {response.status_code} - {response.text}")

    blob_info = response.json()
    return blob_info.get("url", None)
