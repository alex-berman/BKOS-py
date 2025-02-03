from bkos.ontology import *


class LoanApplicationApproved(Proposition):
    pass


class IncomeBelowThreshold(Proposition):
    pass


@dataclass
class Income(Proposition):
    monthly_income: int
