from typing import List

from bkos.domain import Domain
from bkos.hello_world.ontology import *


class DemoDomain(Domain):
    def __init__(self, resources, session_data):
        pass

    def initial_agenda(self) -> List[AgendaItem]:
        return [EmitMove(OfferHelp())]

    def initial_beliefs(self) -> List[Belief]:
        return [Belief(Not(LoanApplicationApproved())), Belief(IncomeBelowThreshold())]

    dependencies = {
        LoanApplicationApproved: {IncomeBelowThreshold}
    }

    def get_support(self, proposition):
        if proposition == Not(LoanApplicationApproved()):
            yield IncomeBelowThreshold()

    def answer_delivery_strategy(self, question) -> AnswerDeliveryStrategy:
        return AnswerDeliveryStrategy.INCREMENTAL if isinstance(question, Why) \
            else AnswerDeliveryStrategy.SINGLE_TURN
