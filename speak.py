from vosk import Model, KaldiRecognizer
import queue
import sounddevice as mic
import espeakng
import os
import json


os.environ["PATH"] = r"C:\Program Files\eSpeak NG;" + os.environ["PATH"]
os.environ["ESPEAK_DATA_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng-data"


en_model: str = '.\\voice_models\\vosk-model-small-en-us-0.15'
fr_model: str = '.\\voice_models\\vosk-model-small-fr-0.22'


q: queue = queue.Queue()  # Due to how this model work it seem to be needed. Would prefer to have it in a function
# but oh well. I might also just be too sleepy to tell other wise.


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def processing_command(command_receive: str, preloaded_commands: dict, speaker: espeakng.Speaker):

    # We should implement a fuzzy hash for the string to see if something is almost exactly a command that exist.
    # some testing will be needed to be sur that if we ask what is a light that it does not close the lights

    for key in preloaded_commands.keys():
        if str(key).lower().strip() != command_receive.lower().strip():
            continue
        speaker.say(preloaded_commands[key]['answer'])
        if str(preloaded_commands[key]['action']).strip().lower() == 'none':
            return
        globals()[str(preloaded_commands[key]['action'])]()  # let's try this. May be better than using a exec.


def VTT(rec: KaldiRecognizer, preloded_command: dict, speaker: espeakng.Speaker):
    with mic.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        listen: bool = True
        print('Voice Transmission activated')
        while listen:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                print(f'Result: {res.get("text")}')
                processing_command(res.get('text'), preloded_command, speaker)
            else:
                print(f'Partial: {rec.PartialResult()}')


# For now I only setup 2 language I will use a bool for simplicity. Will probably change to an enum if I decide to
# make it better
def init_VTT_model(is_english:bool=True, SAMPLE_RATE:int = 16000, ) -> KaldiRecognizer:
    language: str = en_model if is_english else fr_model
    model:Model = Model(en_model)
    return KaldiRecognizer(model, SAMPLE_RATE)


def speak(speaker: espeakng.Speaker, text:str) -> None:
    speaker.say(text, wait4prev=True)


def init_voice() -> espeakng.Speaker:
    mySpeaker = espeakng.Speaker()
    mySpeaker.pitch = 10
    mySpeaker.wpm = 130
    speak(mySpeaker, 'Initialising...')
    return mySpeaker


def voice() -> espeakng.Speaker and KaldiRecognizer:
    return init_voice(), init_VTT_model()