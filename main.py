import json
from speak import voice
from threading import Thread
from queue import Queue, Empty
from eyes import activate_eyes

amount_of_people_visible: int = 0

def load_commands(command_path:str = './order.json'):
    commands: dict = {}
    with open(command_path, 'r') as f:
        commands.update(json.load(f))
    return commands


def audio(preloaded_commands: dict, command_receive: str, answer_queue: Queue):

    # We should implement a fuzzy hash for the string to see if something is almost exactly a command that exist.
    # some testing will be needed to be sur that if we ask what is a light that it does not close the lights

    for key in preloaded_commands.keys():
        if str(key).lower().strip() != command_receive.lower().strip():
            continue
        answer_queue.put(preloaded_commands[key]['answer'])
        if str(preloaded_commands[key]['action']).strip().lower() == 'none':
            return
        globals()[str(preloaded_commands[key]['action'])]()  # let's try this. May be better than using a exec.


def video(amount_of_people: int):
    amount_of_people_visible = amount_of_people


def initialise_audio_thread(queue: Queue, audio_answer_queue, commands:dict):
    Thread(target=voice, args=(commands, queue, audio_answer_queue), daemon=True).start()


def initialise_video_thread(queue:Queue):
    Thread(target=activate_eyes, args=(queue,True), daemon=True).start()


def main():
    commands = load_commands()
    audio_queue: Queue = Queue()
    audio_answer_queue: Queue = Queue()
    video_queue: Queue = Queue()
    initialise_audio_thread(audio_queue,audio_answer_queue, commands)
    initialise_video_thread(video_queue)
    print('All system operational')

    is_active: bool = True
    while is_active:
        try:
            audio_item: str = audio_queue.get(block=True, timeout=0.5)
            audio(commands,audio_item, audio_answer_queue)
        except Empty:
            pass

        try:
            video_item: str = video_queue.get(block=True, timeout=0.5)
            video(int(video_item))  # for now everything should be a integer. may change it later if I start to do more usage
        except Empty:
            pass




if __name__ == '__main__':
    main()