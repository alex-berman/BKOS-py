from bkos.hello_world.ontology import *


def interpret(utterance_cased):
    utterance = utterance_cased.lower()
    tokens = utterance.rstrip('.?!').split(' ')

    if 'approved' in tokens:
        return Ask(BooleanQuestion(LoanApplicationApproved()))
    if 'why' in tokens:
        return Ask(Why())
    if "don't understand" in utterance or 'so what' in utterance:
        return ICM(understanding, negative)
    if utterance == 'ok':
        return ICM(acceptance, positive)
