import json
from speak import voice
from threading import Thread
from queue import Queue, Empty
from eyes import activate_eyes


amount_of_people_visible: int = 0
is_surveillance_mode: bool = False
is_surveillance_order_sent: bool = False

# region pre built actions

# Before we start the multi threading
def video_surveillance():
    global is_surveillance_mode
    is_surveillance_mode = True
    print('Surveillance mode was activated.')


# add logic when there
def stop_video_surveillance():
    is_surveillance_mode = False
    print('Surveillance mode was deactivated')

# endregion


#region complex actions

# Will be use to send information to the owner by email, or text or which ever I will make
# This should activate everytime it see someone while its ensuring no one is there
def surveillance(video_queue_order: Queue):
    global is_surveillance_order_sent, is_surveillance_mode, amount_of_people_visible

    if is_surveillance_mode and amount_of_people_visible > 0 and not is_surveillance_order_sent:
        print('starting video')
        video_queue_order.put(True)
        is_surveillance_order_sent = True

    if amount_of_people_visible <= 0 and is_surveillance_order_sent:
        print('Stopping Video')
        video_queue_order.put(False)
        is_surveillance_order_sent = False

    return


def video(amount_of_people: int):
    global amount_of_people_visible
    amount_of_people_visible = amount_of_people

#endregion


# region load

def load_commands(command_path:str = './order.json'):
    commands: dict = {}
    with open(command_path, 'r') as f:
        commands.update(json.load(f))
    return commands


def run_orders(preloaded_commands: dict, command_receive: str, answer_queue: Queue):

    # We should implement a fuzzy hash for the string to see if something is almost exactly a command that exist.
    # some testing will be needed to be sur that if we ask what is a light that it does not close the lights

    for key in preloaded_commands.keys():
        if str(key).lower().strip() != command_receive.lower().strip():
            continue
        answer_queue.put(preloaded_commands[key]['answer'])
        if str(preloaded_commands[key]['action']).strip().lower() == 'none':
            return
        globals()[str(preloaded_commands[key]['action'])]()  # let's try this. May be better than using a exec.


def initialise_audio_thread(queue: Queue, audio_answer_queue):
    Thread(target=voice, args=(queue, audio_answer_queue), daemon=True).start()


def initialise_video_thread(queue: Queue, video_queue_order: Queue):
    Thread(target=activate_eyes, args=(queue, video_queue_order), daemon=True).start()

# endregion


def main():
    global is_surveillance_mode
    global amount_of_people_visible
    commands = load_commands()
    audio_queue: Queue = Queue()
    audio_answer_queue: Queue = Queue()
    video_queue: Queue = Queue()
    video_queue_order: Queue = Queue()
    initialise_audio_thread(audio_queue, audio_answer_queue)
    initialise_video_thread(video_queue, video_queue_order)
    audio_answer_queue.put('All system operational')

    #TODO remove this when testing is over
    video_surveillance()

    is_active: bool = True
    while is_active:
        #region normal capacity
        try:
            audio_item: str = audio_queue.get(block=True, timeout=0.1)
            run_orders(commands,audio_item, audio_answer_queue)
        except Empty:
            pass

        try:
            video_item = video_queue.get(block=False, timeout=0.1)
            if video_item is not None:
                video(video_item)  # for now everything should be a integer. may change it later if I start to do more usage

        except Empty:
            pass
        #endregion
        #region logic for active activity
        if is_surveillance_mode:
            surveillance(video_queue_order)

        #endregion


if __name__ == '__main__':
    main()
