from bkos.hello_world.types import *


def generate(move):
    if isinstance(move, OfferHelp):
        return 'How can I help?'
    if move == Disconfirm(Not(LoanApplicationApproved())):
        return 'Sorry, your loan application was rejected.'
    if move == Assert(IncomeBelowThreshold()):
        return 'Your income is below the threshold.'
    if move == Assert(Supports(IncomeBelowThreshold(), Not(LoanApplicationApproved()))):
        return 'If the applicant\'s income is too low, a loan cannot be obtained.'
    if isinstance(move, ICM):
        return generate_icm(move)
    raise Exception(f'Failed to generate move {move}')


def generate_icm(move):
    if move.level == acceptance:
        if move.polarity == positive:
            return 'OK.'
    if move.level == understanding and move.polarity == negative:
        return "Sorry, I don't understand."
    raise Exception(f'Failed to generate ICM move {move}')
