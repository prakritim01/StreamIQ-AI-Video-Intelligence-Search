from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import shutil
import os
import json
import mimetypes

from backend.video_processor import analyze_video
from backend.database import SessionLocal, Video, Scene, Detection


app = FastAPI(title="StreamIQ API")


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# DIRECTORIES
# ==========================================

UPLOAD_DIR = "data/videos"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "project": "StreamIQ",
        "status": "running"
    }


# ==========================================
# ANALYZE VIDEO
# ==========================================

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    filename = os.path.basename(file.filename)

    video_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    output_path = os.path.join(
        OUTPUT_DIR,
        filename.rsplit(".", 1)[0] + "_results.json"
    )

    results = analyze_video(
        video_path,
        output_path
    )

    db = SessionLocal()

    try:

        # ==========================================
        # SAVE VIDEO
        # ==========================================

        video = Video(
            filename=filename,
            fps=results["fps"],
            frame_count=results["frame_count"],
            duration=results["duration_seconds"],
            total_detections=results["summary"]["total_detections"],
            object_counts=json.dumps(
                results["summary"]["objects"]
            )
        )

        db.add(video)
        db.commit()
        db.refresh(video)


        # ==========================================
        # SAVE SCENES
        # ==========================================

        for scene_data in results["scenes"]:

            scene = Scene(
                video_id=video.id,
                start_time=scene_data["start"],
                end_time=scene_data["end"],
                objects=json.dumps(
                    scene_data["objects"]
                )
            )

            db.add(scene)


        # ==========================================
        # SAVE YOLO DETECTIONS
        # ==========================================

        for detection_data in results["detections"]:

            timestamp = detection_data["timestamp"]

            for obj in detection_data["objects"]:

                detection = Detection(
                    video_id=video.id,
                    timestamp=timestamp,
                    object_name=obj["name"],
                    confidence=obj["confidence"]
                )

                db.add(detection)


        db.commit()


        # ==========================================
        # RESPONSE
        # ==========================================

        return {
            "message": "Video analyzed and saved",
            "video_id": video.id,
            "filename": video.filename,
            "duration": video.duration,
            "scene_count": len(results["scenes"]),
            "detections": results["summary"]
        }

    finally:

        db.close()


# ==========================================
# GET ALL VIDEOS
# ==========================================

@app.get("/videos")
def get_videos():

    db = SessionLocal()

    try:

        videos = db.query(Video).all()

        return [
            {
                "id": video.id,
                "filename": video.filename,
                "fps": video.fps,
                "frame_count": video.frame_count,
                "duration": video.duration,
                "scene_count": len(video.scenes),
                "total_detections": video.total_detections,
                "object_counts": (
                    json.loads(video.object_counts)
                    if video.object_counts
                    else {}
                )
            }
            for video in videos
        ]

    finally:

        db.close()


# ==========================================
# SERVE VIDEO FILE
# ==========================================

@app.get("/videos/{video_id}/file")
def get_video_file(video_id: int):

    db = SessionLocal()

    try:

        video = (
            db.query(Video)
            .filter(Video.id == video_id)
            .first()
        )

        if not video:

            raise HTTPException(
                status_code=404,
                detail="Video not found"
            )

        filename = os.path.basename(
            video.filename
        )

        video_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        if not os.path.exists(video_path):

            raise HTTPException(
                status_code=404,
                detail="Video file not found on server"
            )

        media_type, _ = mimetypes.guess_type(
            video_path
        )

        if media_type is None:
            media_type = "video/mp4"

        return FileResponse(
            path=video_path,
            media_type=media_type,
            filename=filename
        )

    finally:

        db.close()


# ==========================================
# GET VIDEO DETAILS
# ==========================================

@app.get("/videos/{video_id}")
def get_video(video_id: int):

    db = SessionLocal()

    try:

        video = (
            db.query(Video)
            .filter(Video.id == video_id)
            .first()
        )

        if not video:

            raise HTTPException(
                status_code=404,
                detail="Video not found"
            )

        return {
            "id": video.id,
            "filename": video.filename,
            "fps": video.fps,
            "frame_count": video.frame_count,
            "duration": video.duration,

            "total_detections": (
                video.total_detections or 0
            ),

            "object_counts": (
                json.loads(video.object_counts)
                if video.object_counts
                else {}
            ),

            # ==========================================
            # SCENES
            # ==========================================

            "scenes": [
                {
                    "start": scene.start_time,
                    "end": scene.end_time,
                    "objects": json.loads(
                        scene.objects
                    )
                }
                for scene in video.scenes
            ],

            # ==========================================
            # YOLO DETECTIONS
            # ==========================================

            "detections": [
                {
                    "timestamp": detection.timestamp,
                    "object": detection.object_name,
                    "confidence": detection.confidence
                }
                for detection in sorted(
                    video.detections,
                    key=lambda d: d.timestamp
                )
            ]
        }

    finally:

        db.close()