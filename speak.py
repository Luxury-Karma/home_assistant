from vosk import Model, KaldiRecognizer
import queue
import sounddevice as mic
import espeakng
import os
import json
from queue import Queue, Empty


os.environ["PATH"] = r"C:\Program Files\e__speak NG;" + os.environ["PATH"]
os.environ["ESPEAK_DATA_PATH"] = r"C:\Program Files\e__speak NG\e__speak-ng-data"


en_model: str = '.\\voice_models\\vosk-model-small-en-us-0.15'
fr_model: str = '.\\voice_models\\vosk-model-small-fr-0.22'


initial_audio_queue: Queue = Queue()  # Due to how this model work it seem to be needed. Would prefer to have it in a function
# but oh well. I might also just be too sleepy to tell other wise.


def __callback(in_data, frames, time, status):
    initial_audio_queue.put(bytes(in_data))


def __VTT(rec: KaldiRecognizer, answer_queue: Queue, command_queue: Queue, speaker: espeakng):
    with mic.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=__callback):
        listen: bool = True
        print('Voice Transmission activated')
        while listen:
            # Could make this its own thread to be able to listen while the assistant __speak. But for now let's keep this simple
            try:
                order: str = answer_queue.get(block=False, timeout=0.1)
                __speak(speaker, order)
            except Empty:
                pass

            data = initial_audio_queue.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                print(f'Result: {res.get("text")}')
                command_queue.put(res.get('text'))
            else:
                continue
                #print(f'Partial: {rec.PartialResult()}')


# For now I only setup 2 language I will use a bool for simplicity. Will probably change to an enum if I decide to
# make it better
def __init_VTT_model(is_english:bool=True, SAMPLE_RATE:int = 16000, ) -> KaldiRecognizer:
    language: str = en_model if is_english else fr_model
    model:Model = Model(en_model)
    return KaldiRecognizer(model, SAMPLE_RATE)


def __speak(speaker: espeakng.Speaker, text:str) -> None:
    speaker.say(text, wait4prev=True)


def __init_voice() -> espeakng.Speaker:
    model = espeakng.Speaker()
    model.pitch = 10
    model.wpm = 130
    __speak(model, 'Initialising...')
    return model


def voice(command_queue: Queue, answer_queue: Queue) -> espeakng.Speaker and KaldiRecognizer:
    __VTT(__init_VTT_model(), answer_queue=answer_queue, command_queue=command_queue, speaker=__init_voice())
