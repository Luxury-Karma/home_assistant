import json
from speak import voice
from threading import Thread


def load_commands(command_path:str = './order.json'):
    commands: dict = {}
    with open(command_path, 'r') as f:
        commands.update(json.load(f))
    return commands


def main():
    voice(load_commands())


if __name__ == '__main__':
    main()