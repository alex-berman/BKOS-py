import readline # noqa
import logging
import argparse

from bkos import bot
from bkos.ontology import UserInput
import bkos.hello_world.domain
import bkos.hello_world.nlu
import bkos.hello_world.nlg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", default=logging.WARNING)
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)
    resources = {
        'domain_class': bkos.hello_world.domain.HelloWorldDomain,
        'nlu': bkos.hello_world.nlu,
        'nlg': bkos.hello_world.nlg,
    }
    state = bot.initiate_dialog_state(resources)
    while True:
        system_utterance = bot.get_response(resources, state)
        print(f'S: {system_utterance}')
        user_utterance = input('U: ')
        state.user_input = UserInput(utterance=user_utterance)
