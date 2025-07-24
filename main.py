import json
from speak import VTT, voice


def load_commands(command_path:str = './order.json'):
    commands: dict = {}
    with open(command_path, 'r') as f:
        commands.update(json.load(f))
    return commands

def main():
    speaker, rec = voice()
    VTT(rec, load_commands(),speaker)
    return


if __name__ == '__main__':
    main()