from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    inspect,
    text
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship
)


# ==================================================
# DATABASE
# ==================================================

DATABASE_URL = "sqlite:///./streamiq.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ==================================================
# VIDEO
# ==================================================

class Video(Base):

    __tablename__ = "videos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    fps = Column(
        Float
    )

    frame_count = Column(
        Integer
    )

    duration = Column(
        Float
    )

    # Total number of YOLO detections
    total_detections = Column(
        Integer,
        default=0
    )

    # JSON string containing object counts
    object_counts = Column(
        String,
        default="{}"
    )

    scenes = relationship(
        "Scene",
        back_populates="video",
        cascade="all, delete-orphan"
    )

    detections = relationship(
        "Detection",
        back_populates="video",
        cascade="all, delete-orphan"
    )


# ==================================================
# SCENE
# ==================================================

class Scene(Base):

    __tablename__ = "scenes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    video_id = Column(
        Integer,
        ForeignKey("videos.id")
    )

    start_time = Column(
        Float
    )

    end_time = Column(
        Float
    )

    objects = Column(
        String
    )

    video = relationship(
        "Video",
        back_populates="scenes"
    )


# ==================================================
# DETECTION
#
# Stores every timestamped YOLO detection.
#
# Example:
#
#  video_id = 5
#  timestamp = 4.25
#  object_name = "car"
#  confidence = 0.91
#
# This allows StreamIQ to create an
# interactive AI detection timeline.
# ==================================================

class Detection(Base):

    __tablename__ = "detections"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    video_id = Column(
        Integer,
        ForeignKey("videos.id"),
        nullable=False,
        index=True
    )

    timestamp = Column(
        Float,
        nullable=False,
        index=True
    )

    object_name = Column(
        String,
        nullable=False,
        index=True
    )

    confidence = Column(
        Float
    )

    video = relationship(
        "Video",
        back_populates="detections"
    )


# ==================================================
# CREATE TABLES
# ==================================================

Base.metadata.create_all(
    bind=engine
)


# ==================================================
# DATABASE MIGRATION
#
# Adds new columns to existing databases.
# Existing videos are NOT deleted.
# ==================================================

def migrate_database():

    inspector = inspect(engine)

    # ----------------------------------------------
    # Videos table
    # ----------------------------------------------

    video_columns = [
        column["name"]
        for column in inspector.get_columns("videos")
    ]

    with engine.begin() as connection:

        if "total_detections" not in video_columns:

            connection.execute(
                text(
                    "ALTER TABLE videos "
                    "ADD COLUMN total_detections INTEGER DEFAULT 0"
                )
            )

        if "object_counts" not in video_columns:

            connection.execute(
                text(
                    "ALTER TABLE videos "
                    "ADD COLUMN object_counts TEXT DEFAULT '{}'"
                )
            )


# Run migration
migrate_database()