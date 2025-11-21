import os
import httpx

VERCEL_BLOB_API = "https://api.vercel.com/v2/blob/upload"
VERCEL_TOKEN = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")
BUCKET = os.getenv("VERCEL_BLOB_BUCKET_NAME", "default")


async def put(path: str, data: bytes, content_type: str, access="public"):
    """
    Uploads file to Vercel Blob (binary-safe).
    Returns public download URL.
    """

    if not VERCEL_TOKEN:
        raise RuntimeError("Missing VERCEL_BLOB_READ_WRITE_TOKEN")

    # ensure bytes
    if isinstance(data, str):
        data = data.encode("utf-8")

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "x-vercel-bucket": BUCKET,
        "x-vercel-content-type": content_type,
        "x-vercel-access": access,
        "x-vercel-content-disposition": f'attachment; filename="{os.path.basename(path)}"',
    }

    params = {"slug": path}

    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.put(
            VERCEL_BLOB_API,
            params=params,
            content=data,
            headers=headers
        )

    if res.status_code not in (200, 201):
        raise RuntimeError(f"Vercel Blob upload failed {res.status_code}: {res.text}")

    return res.json().get("url")
