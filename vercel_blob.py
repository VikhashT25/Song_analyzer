import os
import httpx

VERCEL_BLOB_API = "https://api.vercel.com/v2/blob"

# Correct token loading
VERCEL_TOKEN = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")
BUCKET = os.getenv("VERCEL_BLOB_BUCKET_NAME", "default")

async def put(path: str, data: bytes, content_type: str, access: str = "public"):
    """
    Uploads file to Vercel Blob (binary safe).
    """

    if not VERCEL_TOKEN:
        raise RuntimeError("Missing VERCEL_BLOB_READ_WRITE_TOKEN in .env")

    if isinstance(data, str):
        data = data.encode("utf-8")

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "x-vercel-blob-bucket": BUCKET,
        "x-vercel-blob-content-type": content_type,
        "x-vercel-blob-access": access,
        "x-vercel-blob-content-disposition": f'attachment; filename="{os.path.basename(path)}"',
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.put(
            f"{VERCEL_BLOB_API}/filename",
            content=data,
            headers=headers
        )

    if res.status_code not in (200, 201):
        raise RuntimeError(f"Blob upload failed {res.status_code}: {res.text}")

    return res.json()["url"]
