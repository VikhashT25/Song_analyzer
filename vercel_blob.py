# vercel_blob.py
import os
import httpx
import asyncio

# ⚙️ Your Blob base URL (from Vercel → Storage → Blob)
VERCEL_BLOB_URL = "https://fbgruph4dru1oifl.public.blob.vercel-storage.com"

# ⚙️ Token from Environment Variables (set in Vercel Dashboard)
VERCEL_TOKEN = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")


async def put(path: str, data: bytes, content_type: str, access: str = "public"):
    """
    Upload a file to Vercel Blob Storage.
    Returns the full public URL.
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

    # ✅ Return directly constructed public URL (for universal reliability)
    return f"{VERCEL_BLOB_URL}/{path}"
