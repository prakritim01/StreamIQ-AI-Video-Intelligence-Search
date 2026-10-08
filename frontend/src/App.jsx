import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [videos, setVideos] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedObject, setSelectedObject] = useState("all");

  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  // ==========================================
  // LOAD VIDEOS
  // ==========================================

  const loadVideos = async () => {
    try {
      const response = await fetch(`${API_URL}/videos`);
      const data = await response.json();

      setVideos(data);

      if (data.length > 0) {
        loadVideoDetails(data[data.length - 1].id);
      }
    } catch (error) {
      console.error("Failed to load videos:", error);
    }
  };

  // ==========================================
  // LOAD VIDEO DETAILS
  // ==========================================

  const loadVideoDetails = async (id) => {
    try {
      const response = await fetch(
        `${API_URL}/videos/${id}`
      );

      const data = await response.json();

      setSelectedVideo(data);
      setSelectedObject("all");
    } catch (error) {
      console.error("Failed to load video:", error);
    }
  };

  useEffect(() => {
    loadVideos();
  }, []);

  // ==========================================
  // UPLOAD VIDEO
  // ==========================================

  const handleFileChange = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    await analyzeVideo(file);
  };

  const handleDrop = async (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files[0];

    if (!file) return;

    await analyzeVideo(file);
  };

  const analyzeVideo = async (file) => {
    setLoading(true);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/analyze`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Analysis failed"
        );
      }

      await loadVideos();

      await loadVideoDetails(data.video_id);

    } catch (error) {
      console.error(error);
      alert("Video analysis failed.");
    }

    setLoading(false);
  };

  // ==========================================
  // JUMP TO VIDEO TIMESTAMP
  // ==========================================

  const jumpToTime = (seconds) => {
    if (!videoRef.current) return;

    videoRef.current.currentTime = seconds;

    videoRef.current.play().catch(() => {});
  };

  // ==========================================
  // GROUP DETECTIONS BY TIMESTAMP
  // ==========================================

  const groupedDetections = () => {
    if (
      !selectedVideo ||
      !selectedVideo.detections
    ) {
      return [];
    }

    const groups = {};

    selectedVideo.detections.forEach(
      (detection) => {
        const timestamp =
          Number(detection.timestamp).toFixed(2);

        if (!groups[timestamp]) {
          groups[timestamp] = {
            timestamp: Number(timestamp),
            objects: []
          };
        }

        groups[timestamp].objects.push(
          detection
        );
      }
    );

    let result = Object.values(groups);

    if (selectedObject !== "all") {
      result = result.filter((group) =>
        group.objects.some(
          (detection) =>
            detection.object === selectedObject
        )
      );
    }

    return result;
  };

  // ==========================================
  // OBJECT COUNTS
  // ==========================================

  const objectCounts =
    selectedVideo?.object_counts || {};

  const objectNames =
    Object.keys(objectCounts);

  const totalObjects =
    selectedVideo?.total_detections || 0;

  const detectionPoints =
    groupedDetections();

  // ==========================================
  // RENDER
  // ==========================================

  return (
    <div className="app">

      {/* ======================================
          NAVBAR
      ====================================== */}

      <nav className="navbar">

        <div className="brand">
          <div className="brand-mark">
            SQ
          </div>

          <div>
            <div className="brand-name">
              StreamIQ
            </div>

            <div className="brand-subtitle">
              AI Video Intelligence
            </div>
          </div>
        </div>

        <div className="nav-status">
          <span className="status-dot"></span>
          AI Engine Online
        </div>

      </nav>


      {/* ======================================
          HERO
      ====================================== */}

      <section className="hero">

        <div className="hero-content">

          <span className="eyebrow">
            INTELLIGENT VIDEO ANALYTICS
          </span>

          <h1>
            Turn video into
            <span> searchable intelligence.</span>
          </h1>

          <p>
            Upload a video and let StreamIQ detect
            objects, analyze scenes, and create
            timestamped AI insights automatically.
          </p>

        </div>

      </section>


      {/* ======================================
          UPLOAD
      ====================================== */}

      <main className="main-container">

        <section
          className="upload-card"
          onDragOver={(event) =>
            event.preventDefault()
          }
          onDrop={handleDrop}
        >

          <div className="upload-icon">
            ↑
          </div>

          <h2>
            Analyze a video
          </h2>

          <p>
            Drag and drop your video here, or
            choose a file from your computer.
          </p>

          <button
            className="primary-button"
            onClick={() =>
              fileInputRef.current.click()
            }
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Choose Video"}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            hidden
          />

        </section>


        {/* ====================================
            DASHBOARD
        ==================================== */}

        {selectedVideo && (

          <section className="dashboard">

            {/* ==================================
                VIDEO LIST
            ================================== */}

            <div className="dashboard-header">

              <div>
                <span className="section-label">
                  VIDEO LIBRARY
                </span>

                <h2>
                  Your analyzed videos
                </h2>
              </div>

              <span className="video-count">
                {videos.length} video
                {videos.length !== 1
                  ? "s"
                  : ""}
              </span>

            </div>


            <div className="video-list">

              {videos.map((video) => (

                <button
                  key={video.id}
                  className={
                    selectedVideo.id === video.id
                      ? "video-item active"
                      : "video-item"
                  }
                  onClick={() =>
                    loadVideoDetails(video.id)
                  }
                >

                  <div className="video-item-icon">
                    ▶
                  </div>

                  <div className="video-item-info">

                    <strong>
                      {video.filename}
                    </strong>

                    <span>
                      {video.duration}s ·{" "}
                      {video.total_detections}
                      {" "}detections
                    </span>

                  </div>

                </button>

              ))}

            </div>


            {/* ==================================
                ANALYSIS HEADER
            ================================== */}

            <div className="analysis-header">

              <div>

                <span className="section-label">
                  AI ANALYSIS
                </span>

                <h2>
                  {selectedVideo.filename}
                </h2>

              </div>

              <div className="analysis-badge">
                YOLO Detection
              </div>

            </div>


            {/* ==================================
                VIDEO PLAYER
            ================================== */}

            <div className="player-section">

              <div className="video-player-wrapper">

                <video
                  ref={videoRef}
                  key={selectedVideo.id}
                  className="video-player"
                  src={`${API_URL}/videos/${selectedVideo.id}/file`}
                  controls
                  preload="metadata"
                />

              </div>

            </div>


            {/* ==================================
                STATS
            ================================== */}

            <div className="stats-grid">

              <div className="stat-card">

                <span>
                  DURATION
                </span>

                <strong>
                  {selectedVideo.duration}s
                </strong>

              </div>

              <div className="stat-card">

                <span>
                  SCENES
                </span>

                <strong>
                  {selectedVideo.scenes?.length || 0}
                </strong>

              </div>

              <div className="stat-card">

                <span>
                  OBJECT TYPES
                </span>

                <strong>
                  {objectNames.length}
                </strong>

              </div>

              <div className="stat-card">

                <span>
                  DETECTIONS
                </span>

                <strong>
                  {totalObjects}
                </strong>

              </div>

            </div>


            {/* ==================================
                DETECTED OBJECTS
            ================================== */}

            <div className="objects-section">

              <div className="section-heading">

                <div>

                  <span className="section-label">
                    COMPUTER VISION
                  </span>

                  <h3>
                    Detected objects
                  </h3>

                </div>

              </div>


              <div className="object-grid">

                {Object.entries(objectCounts).map(
                  ([name, count]) => (

                    <button
                      key={name}
                      className={
                        selectedObject === name
                          ? "object-card selected"
                          : "object-card"
                      }
                      onClick={() =>
                        setSelectedObject(
                          selectedObject === name
                            ? "all"
                            : name
                        )
                      }
                    >

                      <span className="object-name">
                        {name}
                      </span>

                      <strong>
                        {count}
                      </strong>

                    </button>

                  )
                )}

              </div>

            </div>


            {/* ==================================
                AI DETECTION TIMELINE
            ================================== */}

            <div className="detection-section">

              <div className="section-heading">

                <div>

                  <span className="section-label">
                    TIMESTAMPED INTELLIGENCE
                  </span>

                  <h3>
                    AI Detection Timeline
                  </h3>

                  <p>
                    Click any detection point to
                    jump directly to that moment
                    in the video.
                  </p>

                </div>

                <div className="timeline-count">
                  {detectionPoints.length}{" "}
                  timestamps
                </div>

              </div>


              {/* FILTERS */}

              <div className="timeline-filters">

                <button
                  className={
                    selectedObject === "all"
                      ? "filter-button active"
                      : "filter-button"
                  }
                  onClick={() =>
                    setSelectedObject("all")
                  }
                >
                  All objects
                </button>

                {objectNames.map((name) => (

                  <button
                    key={name}
                    className={
                      selectedObject === name
                        ? "filter-button active"
                        : "filter-button"
                    }
                    onClick={() =>
                      setSelectedObject(name)
                    }
                  >
                    {name}
                  </button>

                ))}

              </div>


              {/* TIMELINE */}

              <div className="detection-timeline">

                <div className="timeline-track">

                  <div className="timeline-start">
                    0s
                  </div>

                  <div className="timeline-end">
                    {selectedVideo.duration}s
                  </div>


                  {detectionPoints.map(
                    (point, index) => {

                      const left =
                        selectedVideo.duration > 0
                          ? (point.timestamp /
                              selectedVideo.duration) *
                            100
                          : 0;

                      return (

                        <button
                          key={`${point.timestamp}-${index}`}
                          className="detection-marker"
                          style={{
                            left: `${left}%`
                          }}
                          onClick={() =>
                            jumpToTime(
                              point.timestamp
                            )
                          }
                          title={`${point.timestamp}s`}
                        >

                          <span className="marker-dot">
                          </span>

                          <span className="marker-tooltip">

                            <strong>
                              {point.timestamp}s
                            </strong>

                            <span>

                              {[
                                ...new Set(
                                  point.objects.map(
                                    (obj) =>
                                      obj.object
                                  )
                                )
                              ].join(", ")}

                            </span>

                          </span>

                        </button>

                      );
                    }
                  )}

                </div>

              </div>


              {/* DETECTION EVENTS */}

              <div className="detection-events">

                {detectionPoints
                  .slice(0, 12)
                  .map((point, index) => (

                    <button
                      key={`${point.timestamp}-${index}`}
                      className="detection-event"
                      onClick={() =>
                        jumpToTime(
                          point.timestamp
                        )
                      }
                    >

                      <div className="event-time">
                        {point.timestamp}s
                      </div>

                      <div className="event-objects">

                        {[
                          ...new Set(
                            point.objects.map(
                              (obj) =>
                                obj.object
                            )
                          )
                        ].map((object) => (

                          <span
                            key={object}
                            className="event-tag"
                          >
                            {object}
                          </span>

                        ))}

                      </div>

                    </button>

                  ))}

              </div>

            </div>


            {/* ==================================
                SCENE TIMELINE
            ================================== */}

            <div className="scenes-section">

              <div className="section-heading">

                <div>

                  <span className="section-label">
                    VIDEO STRUCTURE
                  </span>

                  <h3>
                    Scene Timeline
                  </h3>

                </div>

              </div>


              <div className="scene-timeline">

                {selectedVideo.scenes?.map(
                  (scene, index) => {

                    const left =
                      selectedVideo.duration > 0
                        ? (scene.start /
                            selectedVideo.duration) *
                          100
                        : 0;

                    const width =
                      selectedVideo.duration > 0
                        ? ((scene.end -
                            scene.start) /
                            selectedVideo.duration) *
                          100
                        : 100;

                    return (

                      <button
                        key={index}
                        className="scene-marker"
                        style={{
                          left: `${left}%`,
                          width: `${Math.max(
                            width,
                            2
                          )}%`
                        }}
                        onClick={() =>
                          jumpToTime(
                            scene.start
                          )
                        }
                        title={`Scene ${
                          index + 1
                        }`}
                      >
                        Scene {index + 1}
                      </button>

                    );

                  }
                )}

              </div>


              <div className="scene-cards">

                {selectedVideo.scenes?.map(
                  (scene, index) => (

                    <div
                      className="scene-card"
                      key={index}
                    >

                      <div className="scene-number">
                        {String(index + 1).padStart(
                          2,
                          "0"
                        )}
                      </div>

                      <div className="scene-info">

                        <strong>
                          {scene.start}s
                          {" — "}
                          {scene.end}s
                        </strong>

                        <div className="scene-tags">

                          {scene.objects.map(
                            (object) => (

                              <span
                                key={object}
                              >
                                {object}
                              </span>

                            )
                          )}

                        </div>

                      </div>

                      <button
                        className="scene-jump"
                        onClick={() =>
                          jumpToTime(
                            scene.start
                          )
                        }
                      >
                        ▶ Jump
                      </button>

                    </div>

                  )
                )}

              </div>

            </div>

          </section>

        )}

      </main>

    </div>
  );
}

export default App;