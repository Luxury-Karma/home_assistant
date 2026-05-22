import json
from multiprocessing.connection import answer_challenge

from speak import voice
from threading import Thread
from queue import Queue, Empty
from eyes import activate_eyes
from mind import request_llm_answer


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

    text = command_receive.strip()

    for key, value in preloaded_commands.items():
        key_lower = key.lower()
        if text.lower().startswith(key_lower):
            argument = text[len(key):].strip()  # everything after command

            answer_queue.put(value['answer'])

            action = str(value.get('action', 'none')).lower().strip()

            if action != "none":
                if globals()[action] == deep_research_for_question:
                    globals()[action](argument, answer_queue)
                globals()[action]()  # pass argument here

            return



def deep_research_for_question(question: str, answer_queue: Queue):
    """
    This is a joke its just running the LLM on the followed sentences
    :return:
    """
    data:dict = {
        "model": "deepseek-r1:8b",  # Replace with your model name (e.g., "deepseek", "llama2", etc.)
        "prompt": f'{question} Keep it short. This will be read out for someone.',
        "stream": False  # Set to False to get the entire response at once
    }
    request = request_llm_answer(data)
    answer_queue.put(request)
    return


def initialise_audio_thread(queue: Queue, audio_answer_queue):
    Thread(target=voice, args=(queue, audio_answer_queue), daemon=True).start()


def initialise_video_thread(queue: Queue, video_queue_order: Queue, testing_mode: bool = True):
    Thread(
        target=activate_eyes,
        kwargs={
            "vision_queue": queue,
            "control_queue": video_queue_order,
            "testing_mode": testing_mode
        },
        daemon=True
    ).start()
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
