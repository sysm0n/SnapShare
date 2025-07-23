<div style="display:flex;align-items:center;gap:16px;">
  <img src="frontend/logo.png" alt="SnapShare Logo" width="48" />
  <h1 style="margin:0;">SnapShare: Event Photo Gallery</h1>
</div>

A modern FastAPI web application for event photo sharing with S3/MinIO cloud storage, user identification, and privacy options.

## Features
- Customizable event name (via environment variable)
- User identification (enter name, stored in cookie)
- Photo upload (camera and gallery)
- S3/MinIO integration for cloud storage
- Privacy option: show only own photos or all
- Mobile-friendly, clean UI
- Dockerized deployment

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/sysm0n/snapshare.git
cd snapshare
```

### 2. Configure environment variables
Edit `docker-compose.yml` to set your event name, S3/MinIO credentials, and privacy settings:
```yaml
  environment:
    - EVENT_NAME=Event Name
    - S3_ENDPOINT=minio:9000
    - S3_ACCESS_KEY=ROOTNAME
    - S3_SECRET_KEY=CHANGEME123
    - S3_BUCKET=event1
    - SHOW_ONLY_OWN_PHOTOS=true
```

### 3. Build and run with Docker Compose
```bash
docker-compose up --build
```

The app will be available at [http://localhost:8000](http://localhost:8000)

MinIO Console: [http://localhost:9001](http://localhost:9001)

### 4. Usage
- Open the app in your browser
- Enter your name to start uploading and viewing photos
- Use the camera or gallery upload buttons
- Gallery updates in real time
- If privacy is enabled, you only see your own photos

## Customization
- Change event name and privacy in `docker-compose.yml`
- Use your own S3/MinIO credentials
- Style the UI in `frontend/style.css`

## License
MIT

---
Made with ❤️ for events and memories.
