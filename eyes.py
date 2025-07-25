import cv2
from ultralytics import YOLO
from statistics import mode
from queue import Queue, Empty
import datetime

"""
@software{yolo11_ultralytics,
  author = {Glenn Jocher and Jing Qiu},
  title = {Ultralytics YOLO11},
  version = {11.0.0},
  year = {2024},
  url = {https://github.com/ultralytics/ultralytics},
  orcid = {0000-0001-5950-6979, 0000-0003-3783-7069},
  license = {AGPL-3.0}
}
"""

is_recording: bool = False


def __initialise_eyes(webcam_int: int = 0, model_path: str = '.\\eyes_model\\yolo11n.pt') -> cv2.VideoCapture and YOLO:
    return cv2.VideoCapture(webcam_int), YOLO(model_path)


def __make_save_file_name() -> str:
    date = str(datetime.datetime.now())
    date = date.replace(' ', '_')
    date = date.replace(':', '.')
    return date


def frame_modification(amount_of_person: list, frame):
    for r in amount_of_person:
        x1, y1, x2, y2 = map(int, r.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(frame, f"People: {len(amount_of_person)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    # Add timestamp at bottom-left
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0),
                2, cv2.LINE_AA)


def __scan_for_people(model: YOLO, webcam: cv2, queue: Queue, video_queue_order, testing_mode: bool = False, frames_to_consider: int = 6, minimal_confidence: float = 0.7):
    global is_recording
    capture: bool = True
    last_frames_amount: list[int] = []
    people_in_camera: int = 0  # will be passed to know the amount of people the skull see and if he speak to one or multiple people
    # could also be use in the security mode to tell how many people he saw plus sending picture/video
    video_writer: cv2.VideoWriter = None

    while capture:
        ret, frame = webcam.read()
        if not ret:
            print('error with the video flux.\nSTOPPING.')
            break
        results = model.track(frame, verbose=False, conf=minimal_confidence)[0]
        amount_of_person: list = [r for r in results.boxes if int(r.cls) == 0]  # 0 with YOLO is person.
        last_frames_amount.append(len(amount_of_person))

        if len(last_frames_amount) >= frames_to_consider:
            last_frames_amount.pop(0)
            queue.put(mode(last_frames_amount))

        try:
            recording: bool = video_queue_order.get(block=True, timeout=0.01)
            if not recording and is_recording and video_writer and recording != None:
                print(f'reccording : {recording} \n is_recording {is_recording} \n video_writer : {video_writer} \n reccording : {recording}')
                video_writer.release()
                video_writer = None
                print('Stopped video')

            is_recording = recording
            video_queue_order.empty()

        except Empty:
            pass

        if is_recording:
            if video_writer is None:
                width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = webcam.get(cv2.CAP_PROP_FPS)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                file_name: str = __make_save_file_name()
                video_writer = cv2.VideoWriter(f".\\security_camera_video\\{file_name}.mp4", fourcc, fps, (width, height))
                print(f"Started recording to {file_name}.mp4")

            frame_modification(amount_of_person, frame)

            video_writer.write(frame)

        if testing_mode:
            __testing_visual_webcam(amount_of_person, frame)


def __testing_visual_webcam(amount_of_person: list, frame):
    frame_modification(amount_of_person, frame)
    cv2.imshow("Live Person Detection", frame)
    cv2.waitKey(1)


def activate_eyes(queue: Queue, video_queue_order: Queue, testing_mode: bool = False):
    if testing_mode:
        print('Testing mode activated for the "eye" component"')
    webcam, model = __initialise_eyes()
    __scan_for_people(model, webcam, queue, video_queue_order, testing_mode)


