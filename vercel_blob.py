import os
import httpx

VERCEL_BLOB_API = "https://api.vercel.com/v2/blob"
VERCEL_TOKEN = os.getenv("vercel_blob_rw_FBGRUPH4dru1OiFl_KSYSeGnajKDumgbQ7OO8SXXF9cjACv")  # correct
BUCKET = os.getenv("VERCEL_BLOB_BUCKET_NAME", "default")


async def put(path: str, data: bytes, content_type: str):
    """
    Uploads file to Vercel Blob (binary-safe).
    Returns public download URL.
    """

    if not VERCEL_TOKEN:
        raise RuntimeError("Missing VERCEL_BLOB_READ_WRITE_TOKEN")

    # Ensure data is bytes
    if isinstance(data, str):
        data = data.encode("utf-8")

    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "x-vercel-blob-bucket": BUCKET,
        "x-vercel-blob-content-type": content_type,
        "x-vercel-blob-access": "public",
        "x-vercel-blob-content-disposition": f'attachment; filename="{os.path.basename(path)}"',
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.put(
            f"{VERCEL_BLOB_API}/upload?slug={path}",
            content=data,
            headers=headers
        )

    if res.status_code not in (200, 201):
        raise RuntimeError(f"Blob upload failed ({res.status_code}): {res.text}")

    return res.json()["url"]
