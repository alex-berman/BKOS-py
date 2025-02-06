from hello_world.ontology import *


def generate(move):
    if isinstance(move, OfferHelp):
        return 'How can I help?'
    if move == Disconfirm(Not(LoanApplicationApproved())):
        return 'Sorry, your loan application was rejected.'
    if move == Assert(IncomeBelowThreshold()):
        return 'Your income is below the threshold.'
    if move == Assert(Supports(IncomeBelowThreshold(), Not(LoanApplicationApproved()))):
        return 'If the applicant\'s income is too low, a loan cannot be obtained.'
    raise Exception(f'Failed to generate move {move}')
