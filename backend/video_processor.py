import cv2
import json
from collections import Counter
from ultralytics import YOLO

model = YOLO("yolo11n.pt")


def analyze_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps else 0

    results = {
        "video": video_path,
        "fps": round(fps, 2),
        "frame_count": frame_count,
        "duration_seconds": round(duration, 2),
        "detections": []
    }

    # Analyze approximately 2 frames per second
    sample_rate = 2
    frame_interval = max(int(fps / sample_rate), 1)

    frame_number = 0

    while True:
        success, frame = cap.read()

        if not success:
            break

        if frame_number % frame_interval == 0:

            timestamp = frame_number / fps if fps else 0

            prediction = model(frame, verbose=False)[0]

            objects = []

            for box in prediction.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]

                if confidence >= 0.30:

                    objects.append({
                        "name": class_name,
                        "confidence": round(confidence, 2)
                    })

            if objects:

                results["detections"].append({
                    "timestamp": round(timestamp, 2),
                    "objects": objects
                })

        frame_number += 1

    cap.release()

    # --------------------------------------------------
    # STREAMIQ INTELLIGENCE SUMMARY
    # --------------------------------------------------

    object_counts = Counter()

    for detection in results["detections"]:

        for obj in detection["objects"]:

            object_counts[obj["name"]] += 1

    # Sort objects by frequency
    sorted_objects = object_counts.most_common()

    results["summary"] = {
        "unique_objects": len(object_counts),
        "total_detections": sum(object_counts.values()),
        "objects": dict(sorted_objects)
    }

    # --------------------------------------------------
    # KEY TIMESTAMPS
    # --------------------------------------------------

    key_timestamps = []

    for detection in results["detections"]:

        timestamp = detection["timestamp"]
        objects = detection["objects"]

        # Count unique object types at this timestamp
        unique_types = set(obj["name"] for obj in objects)

        if len(unique_types) >= 3:

            key_timestamps.append({
                "timestamp": timestamp,
                "objects": sorted(unique_types)
            })

    results["key_timestamps"] = key_timestamps
        # --------------------------------------------------
    # SCENE SEGMENTATION
    # --------------------------------------------------

    scenes = []

    if results["detections"]:

        current_scene = {
            "start": results["detections"][0]["timestamp"],
            "end": results["detections"][0]["timestamp"],
            "objects": set()
        }

        previous_timestamp = results["detections"][0]["timestamp"]

        for detection in results["detections"]:

            timestamp = detection["timestamp"]

            # Objects detected at this timestamp
            for obj in detection["objects"]:
                current_scene["objects"].add(obj["name"])

            # If there is a large gap, start a new scene
            if timestamp - previous_timestamp > 1.0:

                scenes.append({
                    "start": round(current_scene["start"], 2),
                    "end": round(current_scene["end"], 2),
                    "objects": sorted(current_scene["objects"])
                })

                current_scene = {
                    "start": timestamp,
                    "end": timestamp,
                    "objects": set()
                }

                for obj in detection["objects"]:
                    current_scene["objects"].add(obj["name"])

            current_scene["end"] = timestamp
            previous_timestamp = timestamp

        # Add final scene
        scenes.append({
            "start": round(current_scene["start"], 2),
            "end": round(current_scene["end"], 2),
            "objects": sorted(current_scene["objects"])
        })

    results["scenes"] = scenes

    # --------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------

    with open(output_path, "w") as f:

        json.dump(
            results,
            f,
            indent=4
        )

    return results


if __name__ == "__main__":

    video_path = "data/videos/sample.mp4"
    output_path = "outputs/results.json"

    results = analyze_video(
        video_path,
        output_path
    )

    print("\n================================")
    print("      STREAMIQ ANALYSIS")
    print("================================")

    print(
        f"Video duration : "
        f"{results['duration_seconds']} seconds"
    )

    print(
        f"Frames         : "
        f"{results['frame_count']}"
    )

    print(
        f"FPS            : "
        f"{results['fps']}"
    )

    print(
        f"Detection points: "
        f"{len(results['detections'])}"
    )

    print("\nDetected objects:")

    for name, count in results["summary"]["objects"].items():

        print(
            f"  {name}: {count}"
        )

    print("\nUnique object types:")

    print(
        results["summary"]["unique_objects"]
    )

    print("\nTotal detections:")

    print(
        results["summary"]["total_detections"]
    )

    print("\nKey timestamps:")

    for item in results["key_timestamps"][:10]:

        print(
            f"  {item['timestamp']}s -> "
            f"{', '.join(item['objects'])}"
        )

    print("\nResults saved to:")

    print(output_path)