# StreamIQ — AI Video Intelligence & Search

> An AI-powered video analysis platform that transforms raw video into structured, timestamped intelligence using computer vision.

StreamIQ allows users to upload videos and automatically extract meaningful visual information using YOLO-based object detection.

The system processes videos, detects objects at specific timestamps, identifies scene segments, stores analytical results in SQLite, and presents the results through an interactive React dashboard.

---

## Overview

Modern video platforms generate enormous amounts of visual data, but manually searching and analyzing that content is slow and difficult.

StreamIQ addresses this problem by converting raw video into searchable visual metadata.

A user uploads a video and StreamIQ:

1. Processes the video with OpenCV.
2. Samples frames at a controlled rate.
3. Runs YOLO object detection.
4. Records detected objects and confidence scores.
5. Associates detections with timestamps.
6. Identifies scene segments.
7. Stores results in a relational SQLite database.
8. Exposes the analysis through a FastAPI backend.
9. Visualizes the results through a React dashboard.
10. Allows users to jump directly to detected events in the video.

---

## Key Features

### 🎥 Video Upload & Processing

- Upload videos directly from the web interface.
- Drag-and-drop support.
- Automatic server-side processing.
- Video metadata extraction including:
  - Duration
  - FPS
  - Frame count

### 🤖 AI Object Detection

StreamIQ uses a pretrained YOLO model to detect objects within sampled video frames.

Detected information includes:

- Object class
- Confidence score
- Timestamp

Example:

```text
4.51s
→ car
→ person
→ truck
```

### ⏱️ Timestamped AI Detection

Every detection is associated with the timestamp at which it occurred.

This creates a temporal representation of the video's visual content.

### 📊 Object Analytics

The dashboard provides:

- Total detections
- Unique object types
- Per-object detection counts
- Object filtering

Example:

```text
car             355
person          138
truck            31
handbag          27
traffic light    11
frisbee           3
```

### 🎬 Scene Segmentation

The system groups continuous detection activity into scene segments.

Each scene stores:

- Start timestamp
- End timestamp
- Objects detected within the scene

### 📍 Interactive AI Detection Timeline

The dashboard provides a visual timeline of AI detections.

Users can:

- View detection events across the video timeline.
- Hover over timestamps to inspect detected objects.
- Filter the timeline by object type.
- Click a detection point to jump directly to that moment in the video.

### ▶️ Integrated Video Player

The analyzed video is served directly by the FastAPI backend and displayed inside the React dashboard.

Detection timestamps are synchronized with the video player.

### 🗄️ Persistent Storage

StreamIQ stores analytical results in SQLite using SQLAlchemy.

The database stores:

- Videos
- Scenes
- Object detections
- Detection timestamps
- Confidence scores
- Object statistics

---

# Architecture

```text
                    ┌──────────────────────┐
                    │      User / UI       │
                    │                      │
                    │     React + Vite     │
                    └──────────┬───────────┘
                               │
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    │                      │
                    │  Upload / Analysis   │
                    │  Video / Results     │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   OpenCV    │ │    YOLO     │ │  SQLite +   │
        │             │ │             │ │  SQLAlchemy │
        │ Video I/O   │ │ Object      │ │             │
        │ Frame       │ │ Detection   │ │ Persistent  │
        │ Sampling    │ │             │ │ Storage     │
        └─────────────┘ └─────────────┘ └─────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Structured Video     │
                    │ Intelligence         │
                    │                      │
                    │ • Objects            │
                    │ • Timestamps         │
                    │ • Confidence         │
                    │ • Scenes              │
                    └──────────────────────┘
```

---

# System Workflow

```text
Video Upload
     │
     ▼
OpenCV Video Reader
     │
     ▼
Frame Sampling
     │
     ▼
YOLO Object Detection
     │
     ├──────────────► Object Classes
     │
     ├──────────────► Confidence Scores
     │
     └──────────────► Timestamps
                         │
                         ▼
                  Scene Segmentation
                         │
                         ▼
                    SQLite Database
                         │
                         ▼
                    FastAPI REST API
                         │
                         ▼
                   React Dashboard
                         │
                         ▼
                Interactive Timeline
```

---

# Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS
- HTML5 Video API

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite

## Computer Vision

- OpenCV
- Ultralytics YOLO

## Development

- Git
- GitHub
- VS Code
- Python virtual environment

---

# Project Structure

```text
StreamIQ/
│
├── backend/
│   ├── database.py
│   ├── main.py
│   └── video_processor.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   └── videos/
│
├── outputs/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Backend Components

## `video_processor.py`

Responsible for video analysis.

Main responsibilities:

- Open video with OpenCV.
- Extract FPS and frame count.
- Calculate video duration.
- Sample frames.
- Run YOLO inference.
- Apply confidence filtering.
- Store timestamped detections.
- Calculate object statistics.
- Generate key timestamps.
- Generate scene segments.
- Save analysis results as JSON.

---

## `database.py`

Defines the SQLAlchemy database schema.

### Video

Stores:

- Filename
- FPS
- Frame count
- Duration
- Total detections
- Object counts

### Scene

Stores:

- Video ID
- Start time
- End time
- Objects present

### Detection

Stores:

- Video ID
- Timestamp
- Object name
- Confidence

---

## `main.py`

Provides the FastAPI REST API.

Main endpoints:

```text
GET  /
POST /analyze
GET  /videos
GET  /videos/{video_id}
GET  /videos/{video_id}/file
```

---

# Frontend Components

The React application provides an interactive dashboard containing:

- Video upload interface
- Video library
- Video player
- Analysis statistics
- Detected object cards
- Object filtering
- AI detection timeline
- Timestamp event cards
- Scene timeline
- Scene jump controls

---

# Detection Pipeline

StreamIQ samples approximately two frames per second from the uploaded video.

For each sampled frame:

```text
Frame
  │
  ▼
YOLO Inference
  │
  ▼
Bounding Boxes
  │
  ▼
Confidence Filtering
  │
  ▼
Object + Confidence
  │
  ▼
Timestamp
  │
  ▼
Database
```

The current detection confidence threshold is:

```text
0.30
```

Detections below this confidence are ignored.

---

# Example Analysis

For a sample video approximately 18 seconds long, StreamIQ produced:

```text
Duration       : 18.02 seconds
Frames         : 432
FPS            : 23.98
Detection      : 40 sampled timestamps
Total objects  : 565
Object types   : 6
```

Detected objects included:

```text
car             355
person          138
truck             31
handbag           27
traffic light     11
frisbee            3
```

These results demonstrate how StreamIQ converts raw video into structured visual metadata.

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/StreamIQ.git
cd StreamIQ
```

---

# Backend Setup

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

---

# Usage

1. Start the FastAPI backend.
2. Start the React frontend.
3. Open the StreamIQ dashboard.
4. Upload a video.
5. Wait for AI analysis to complete.
6. Review object statistics.
7. Inspect the AI Detection Timeline.
8. Filter detections by object.
9. Click a timestamp to jump directly to that point in the video.
10. Explore detected scenes.

---

# Example API Response

A video analysis returns structured metadata similar to:

```json
{
  "message": "Video analyzed and saved",
  "video_id": 1,
  "filename": "sample.mp4",
  "duration": 18.02,
  "scene_count": 1,
  "detections": {
    "unique_objects": 6,
    "total_detections": 565,
    "objects": {
      "car": 355,
      "person": 138,
      "truck": 31,
      "handbag": 27,
      "traffic light": 11,
      "frisbee": 3
    }
  }
}
```

---

# Engineering Highlights

### Efficient Frame Sampling

Instead of running inference on every video frame, StreamIQ samples frames at a controlled rate.

This reduces computational overhead while still generating useful temporal information.

### Structured AI Metadata

Raw YOLO predictions are converted into structured records containing:

```text
timestamp
object
confidence
video_id
```

This makes the analysis queryable rather than simply displaying bounding boxes.

### Separation of Concerns

The system separates:

```text
React UI
   ↓
FastAPI
   ↓
Video Processing
   ↓
Database
```

This allows the computer vision pipeline and frontend to evolve independently.

### Interactive Temporal Search

The detection timeline creates a bridge between AI inference and video playback.

Instead of manually searching through a video, users can navigate directly to AI-generated events.

---

# Future Improvements

Potential future extensions include:

- Semantic video search using CLIP or vision-language models
- Natural-language video queries
- Vector search with FAISS
- PostgreSQL for production-scale storage
- AWS S3 video storage
- Background video processing jobs
- Multi-video search
- Person tracking
- Action recognition
- Automatic scene classification
- Video summarization
- Authentication and user accounts
- Docker deployment
- Cloud deployment

---

# Project Motivation

StreamIQ was designed around a practical problem in modern media and entertainment systems:

> How can large amounts of video content be transformed into structured, searchable information?

The project combines computer vision, backend engineering, database design, and interactive frontend development into a single end-to-end system.

---

# Author

**Prakriti Manhar**

B.Tech — Artificial Intelligence  
SVNIT Surat

GitHub: `prakritim01`

---

# License

This project is intended for educational, research, and portfolio purposes.
