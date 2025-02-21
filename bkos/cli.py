import readline # noqa
import logging
import argparse
import importlib

from bkos import bot
from bkos.types import UserInput


def interact(config):
    resources = config.resources
    state = bot.initiate_dialog_state(resources, config.session_data)
    while True:
        response = bot.get_response(resources, state)
        system_utterance = '' if response is None else response
        print(f'S: {system_utterance}')
        user_utterance = input('U: ')
        state.user_input = UserInput(utterance=user_utterance)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="bkos.hello_world.config")
    parser.add_argument("--log-level", default=logging.WARNING)
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    interact_parser = subparsers.add_parser('interact', help='Run interaction')
    interact_parser.set_defaults(func=interact)
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)
    config = importlib.import_module(args.config)
    args.func(config)
