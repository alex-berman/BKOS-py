from bkos.demo.ontology import *


def generate(move):
    clause = generate_clause(move)
    return initial_upper_case(clause)


def initial_upper_case(s):
    return s[:1].upper() + s[1:] if s else s


def generate_clause(move):
    if isinstance(move, OfferHelp):
        return 'How can I help?'
    if move == Disconfirm(Not(LoanApplicationApproved())):
        return 'sorry, your loan application was rejected.'
    raise Exception(f'Failed to generate clause for move {move}')
