import cv2
from ultralytics import YOLO
from statistics import mode
from queue import Queue, Empty


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


def __initialise_eyes(webcam_int: int = 0, model_path: str = '.\\eyes_model\\yolo11n.pt') -> cv2.VideoCapture and YOLO:
    return cv2.VideoCapture(webcam_int), YOLO(model_path)


def __scan_for_people(model: YOLO, webcam: cv2, queue: Queue, testing_mode: bool = False, frames_to_consider: int = 6, minimal_confidence: float = 0.7):
    capture: bool = True
    last_frames_amount: list[int] = []
    people_in_camera:int = 0  # will be passed to know the amount of people the skull see and if he speak to one or multiple people
    # could also be use in the security mode to tell how many people he saw plus sending picture/video
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
            m = mode(last_frames_amount)
            queue.put(m)


        if testing_mode:
            __testing_visual_webcam(amount_of_person, frame)


def __testing_visual_webcam(amount_of_person: list, frame):
    for r in amount_of_person:
        x1, y1, x2, y2 = map(int, r.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(frame, f"People: {len(amount_of_person)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Live Person Detection", frame)
    cv2.waitKey(1)


def activate_eyes(queue: Queue, testing_mode: bool = False):
    print(f'is in testing mode : {testing_mode}')
    webcam, model = __initialise_eyes()
    __scan_for_people(model, webcam,queue ,testing_mode)


