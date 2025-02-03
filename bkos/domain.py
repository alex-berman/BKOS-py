from abc import ABC, abstractmethod
from typing import List

from bkos.ontology import AgendaItem, Belief, AnswerDeliveryStrategy


class Domain(ABC):
    @abstractmethod
    def initial_agenda(self) -> List[AgendaItem]:
        pass

    @abstractmethod
    def initial_beliefs(self) -> List[Belief]:
        pass

    def answer_delivery_strategy(self, question) -> AnswerDeliveryStrategy:
        return AnswerDeliveryStrategy.SINGLE_TURN

    dependencies = {}
