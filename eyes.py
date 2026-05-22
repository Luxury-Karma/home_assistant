import cv2
import datetime
from ultralytics import YOLO
from statistics import mode
from queue import Queue, Empty


def _init_camera(webcam_index: int = 0):
    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        raise RuntimeError("Camera could not be opened")
    return cap


def _init_model(model_path: str = "./eyes_model/yolo11n.pt"):
    return YOLO(model_path)


def _make_filename():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _draw(frame, people_count, detections):
    # draw boxes
    for det in detections:
        x1, y1, x2, y2 = map(int, det.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # count
    cv2.putText(
        frame,
        f"People: {people_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # timestamp
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        frame,
        ts,
        (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )


def _scan(
    model,
    camera,
    vision_queue: Queue,
    control_queue: Queue,
    testing_mode: bool = False,
    frames_to_consider: int = 6,
    conf: float = 0.7
):
    last_counts = []

    recording = False
    writer = None

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Camera error — stopping vision loop")
            break

        # -------------------------
        # YOLO inference (NO tracking)
        # -------------------------
        results = model.predict(frame, conf=conf, verbose=False)[0]

        people = [r for r in results.boxes if int(r.cls) == 0]
        count = len(people)

        # smoothing
        last_counts.append(count)
        if len(last_counts) > frames_to_consider:
            last_counts.pop(0)

        vision_queue.put(mode(last_counts))

        # -------------------------
        # control signal (safe non-blocking)
        # -------------------------
        try:
            recording_signal = control_queue.get_nowait()

            # only accept bool signals
            if isinstance(recording_signal, bool):
                recording = recording_signal

                if not recording and writer is not None:
                    writer.release()
                    writer = None
                    print("Recording stopped")

        except Empty:
            pass

        # -------------------------
        # start recording
        # -------------------------
        if recording:
            if writer is None:
                h, w = frame.shape[:2]
                fps = camera.get(cv2.CAP_PROP_FPS) or 30

                filename = _make_filename()
                path = f"./security_camera_video/{filename}.mp4"

                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(path, fourcc, fps, (w, h))

                print(f"Recording started: {path}")

            _draw(frame, count, people)
            writer.write(frame)

        # -------------------------
        # testing mode (UI)
        # -------------------------
        if testing_mode:
            _draw(frame, count, people)
            cv2.imshow("Eyes", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    camera.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()


def activate_eyes(
    vision_queue: Queue,
    control_queue: Queue,
    testing_mode: bool = False
):
    camera = _init_camera()
    model = _init_model()

    print("Eyes system started")

    _scan(
        model,
        camera,
        vision_queue,
        control_queue,
        testing_mode=testing_mode
    )