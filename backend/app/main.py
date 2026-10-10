"""
RallyLens AI - Backend API
Member 4: Backend API Lead (Hour 3)
"""

import os
import re
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .schemas import (
    HealthResponse,
    MatchUploadResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    MatchStatusResponse,
    MatchResultsResponse
)
from .jobs import (
    create_match_job,
    get_job,
    start_analysis_task,
    UPLOADS_DIR,
    RESULTS_DIR
)

app = FastAPI(
    title="RallyLens AI API",
    description="Badminton Tactical Analysis & Multi-Frame Tracker API (Hour 3)",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_match_id(match_id: str) -> str:
    """Security check against directory traversal."""
    if not re.match(r"^[a-zA-Z0-9_\-]+$", match_id):
        raise HTTPException(status_code=400, detail="Invalid match ID format")
    return match_id


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health():
    """Service health check."""
    return HealthResponse(status="ok")


@app.post("/api/matches", response_model=MatchUploadResponse, tags=["Matches"])
async def upload_match(file: UploadFile = File(...)):
    """
    Accepts video upload as multipart field named 'file'.
    Returns generated match_id and 'uploaded' status.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    allowed_exts = [".mp4", ".mov", ".avi", ".webm", ".mkv"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format '{ext}'. Allowed: {', '.join(allowed_exts)}"
        )

    # Server-generated safe filename
    file_id = os.urandom(4).hex()
    safe_name = f"{file_id}_{os.path.basename(file.filename)}"
    saved_path = os.path.join(UPLOADS_DIR, safe_name)

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    match_id = create_match_job(file_path=saved_path, filename=file.filename)

    return MatchUploadResponse(
        match_id=match_id,
        status="uploaded",
        filename=file.filename
    )


@app.post("/api/matches/{match_id}/analyze", response_model=AnalyzeResponse, tags=["Matches"])
def start_analysis(
    match_id: str,
    payload: Optional[AnalyzeRequest] = None
):
    """
    Starts analysis with sport, court_corners, and court_type.
    """
    clean_id = _validate_match_id(match_id)
    job = get_job(clean_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Match '{clean_id}' not found")

    sport = payload.sport if payload else "badminton"
    court_corners = payload.court_corners if payload else None
    court_type = payload.court_type if payload else "doubles"

    start_analysis_task(
        match_id=clean_id,
        sport=sport,
        court_corners=court_corners,
        court_type=court_type
    )

    return AnalyzeResponse(
        match_id=clean_id,
        status="queued",
        message="Analysis started on vision pipeline."
    )


@app.get("/api/matches/{match_id}/status", response_model=MatchStatusResponse, tags=["Matches"])
def get_match_status(match_id: str):
    """
    Returns current state: uploaded | queued | processing | completed | failed.
    """
    clean_id = _validate_match_id(match_id)
    if clean_id == "backup_demo":
        return MatchStatusResponse(match_id="backup_demo", status="completed")
    job = get_job(clean_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Match '{clean_id}' not found")

    return MatchStatusResponse(
        match_id=clean_id,
        status=job["status"],
        error=job.get("error")
    )


@app.get("/api/matches/{match_id}/results", tags=["Matches"])
def get_match_results(match_id: str):
    """
    Returns completed metrics, tracks, heatmap, events, warnings, and media URLs.
    Returns 409 if still processing, or 500 if failed.
    """
    clean_id = _validate_match_id(match_id)
    if clean_id == "backup_demo":
        backup_json_path = os.path.join(RESULTS_DIR, "backup_demo", "tracking.json")
        if os.path.exists(backup_json_path):
            import json
            with open(backup_json_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
                backup_data["match_id"] = "backup_demo"
                backup_data["status"] = "completed"
                backup_data["media_urls"] = {
                    "original_video": "/media/backup_demo/video",
                    "annotated_video": "/media/backup_demo/annotated.mp4",
                    "annotated_preview": "/media/backup_demo/annotated_preview.jpg"
                }
                return backup_data

    job = get_job(clean_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Match '{clean_id}' not found")

    if job["status"] in ["queued", "processing"]:
        return JSONResponse(
            status_code=409,
            content={
                "match_id": clean_id,
                "status": job["status"],
                "message": "Analysis is still processing. Please continue polling status."
            }
        )

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {job.get('error')}"
        )

    if not job.get("results"):
        return JSONResponse(
            status_code=409,
            content={
                "match_id": clean_id,
                "status": job.get("status", "processing"),
                "message": "Analysis results are not yet available on disk. Please retry."
            }
        )

    return job["results"]


@app.get("/media/{match_id}/video", tags=["Media"])
def stream_video(match_id: str):
    """Streams original uploaded match video."""
    clean_id = _validate_match_id(match_id)
    if clean_id == "backup_demo":
        sample_path = os.path.join(os.path.dirname(UPLOADS_DIR), "sample.mp4")
        if os.path.exists(sample_path):
            return FileResponse(sample_path, media_type="video/mp4")

    job = get_job(clean_id)
    if job and os.path.exists(job.get("file_path", "")):
        return FileResponse(job["file_path"], media_type="video/mp4")

    # Fallback to annotated video in results folder if available
    annotated_path = os.path.join(RESULTS_DIR, clean_id, "annotated.mp4")
    if os.path.exists(annotated_path):
        return FileResponse(annotated_path, media_type="video/mp4")

    # Fallback to backend sample clip
    sample_path = os.path.join(os.path.dirname(UPLOADS_DIR), "sample.mp4")
    if os.path.exists(sample_path):
        return FileResponse(sample_path, media_type="video/mp4")

    raise HTTPException(status_code=404, detail="Video file not found")


@app.get("/media/{match_id}/annotated.mp4", tags=["Media"])
def stream_annotated_video(match_id: str):
    """Streams annotated video with bounding boxes and player IDs."""
    clean_id = _validate_match_id(match_id)
    out_dir = os.path.join(RESULTS_DIR, clean_id)
    video_path = os.path.join(out_dir, "annotated.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Annotated video not ready")
    return FileResponse(video_path, media_type="video/mp4")


@app.get("/media/{match_id}/annotated_preview.jpg", tags=["Media"])
def get_annotated_preview(match_id: str):
    """Returns annotated image frame."""
    clean_id = _validate_match_id(match_id)
    out_dir = os.path.join(RESULTS_DIR, clean_id)
    img_path = os.path.join(out_dir, "annotated_preview.jpg")
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Annotated preview image not found")
    return FileResponse(img_path, media_type="image/jpeg")
