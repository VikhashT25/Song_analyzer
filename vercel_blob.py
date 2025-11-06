import os
import base64
import httpx

async def put(path: str, content, content_type: str):
    """Uploads any file (string or bytes) to Vercel Blob Storage."""
    vercel_token = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")

    if not vercel_token:
        raise ValueError("Missing VERCEL_BLOB_READ_WRITE_TOKEN environment variable")

    if isinstance(content, str):
        data = content.encode('utf-8')
    else:
        data = content

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.vercel.com/v2/blob/upload?slug={path}",
            headers={
                "Authorization": f"Bearer {vercel_token}",
                "Content-Type": content_type
            },
            content=data
        )
        response.raise_for_status()
        result = response.json()
        return result["url"]
