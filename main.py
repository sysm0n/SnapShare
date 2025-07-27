from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote
import boto3
import os
import mimetypes
import tempfile

# Configuration
EVENT_NAME = os.getenv("EVENT_NAME", "my_event")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "127.0.0.1:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "ROOTNAME")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "CHANGEME123")
S3_BUCKET = os.getenv("S3_BUCKET", "event")
SHOW_ONLY_OWN_PHOTOS = os.getenv("SHOW_ONLY_OWN_PHOTOS", "false").lower() == "true"
USE_BACKGROUND = os.getenv("USE_BACKGROUND", "true").lower() == "true"

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve background.svg from root if it exists
import pathlib
@app.api_route("/background.svg", methods=["GET", "HEAD"])
def background_svg():
    if not USE_BACKGROUND:
        return HTMLResponse(status_code=404, content="Not Found")
    svg_path = pathlib.Path("background.svg")
    if svg_path.exists():
        return FileResponse(str(svg_path), media_type="image/svg+xml")
    return HTMLResponse(status_code=404, content="Not Found")

# S3/MinIO client
s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{S3_ENDPOINT}",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

@app.get("/photos")
def list_photos(request: Request):
    """Return all photos, or only the user's own if SHOW_ONLY_OWN_PHOTOS is set."""
    # Pagination parameters
    try:
        page = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", 10))
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
    except Exception:
        page = 1
        per_page = 10

    user = request.query_params.get("user") if SHOW_ONLY_OWN_PHOTOS else None
    prefix = f"{EVENT_NAME}/"
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    photos = []
    if "Contents" in response:
        for obj in response["Contents"]:
            key = obj["Key"]
            parts = key.split("/")
            if len(parts) >= 3:
                event, photo_user, filename = parts[0], parts[1], "/".join(parts[2:])
                if SHOW_ONLY_OWN_PHOTOS and user and photo_user != user:
                    continue
                url = f"/photo/{quote(key)}"
                photos.append({"user": photo_user, "filename": filename, "url": url})

    total = len(photos)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_photos = photos[start:end]
    return JSONResponse({
        "photos": paginated_photos,
        "total": total,
        "page": page,
        "per_page": per_page
    })

@app.get("/photo/{key:path}")
def get_photo(key: str):
    """Proxy the image from S3/MinIO."""
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    mime_type, _ = mimetypes.guess_type(key)
    if not mime_type:
        mime_type = "application/octet-stream"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(obj["Body"].read())
        tmp.flush()
        return FileResponse(tmp.name, media_type=mime_type)

@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the frontend UI."""
    return open("frontend/index.html").read()

@app.post("/upload")
def upload_photo(user: str = Form(...), file: UploadFile = Form(...)):
    """Upload a photo to S3/MinIO with timestamped filename."""
    import time
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = file.filename if file.filename else f"photo_{timestamp}.jpg"
    filename_parts = filename.rsplit('.', 1)
    if len(filename_parts) == 2:
        name, ext = filename_parts
        new_filename = f"{name}_{timestamp}.{ext}"
    else:
        new_filename = f"{filename}_{timestamp}"
    key = f"{EVENT_NAME}/{user}/{new_filename}"
    s3.upload_fileobj(file.file, S3_BUCKET, key)
    return {"status": "success", "key": key}

@app.get("/config")
def get_config():
    """Return event configuration for frontend."""
    return {
        "event_name": EVENT_NAME,
        "show_only_own_photos": SHOW_ONLY_OWN_PHOTOS,
        "use_background": USE_BACKGROUND
    }
