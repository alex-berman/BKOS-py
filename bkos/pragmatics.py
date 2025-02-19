from bkos.ontology import *
from bkos.semantics import negate_proposition


def is_compatible_with_beliefs(proposition, beliefs, domain):
    for belief in beliefs:
        if belief.proposition == proposition:
            return True
    if isinstance(proposition, Explains):
        supporting_propositions = list(domain.get_support(proposition.explanandum))
        return proposition.explanans in supporting_propositions


def resolve_elliptical_question(question, state):
    if isinstance(question, Why):
        if state.private.continuation:
            for qud in state.shared.qud:
                if isinstance(qud, Why):
                    return qud
        elif isinstance(state.previous_system_move, Constative):
            return Why(state.previous_system_move.proposition)


def get_answers(question, beliefs, domain):
    if isinstance(question, Why):
        explanations = select_explanations(question.explanandum, beliefs, domain)
        for explanation in explanations:
            yield explanation
    if isinstance(question, BooleanQuestion):
        if isinstance(question.proposition, Supports):
            if any([supporting_proposition
                    for supporting_proposition in domain.get_support(question.proposition.consequent)
                    if question.proposition.antecedent == supporting_proposition]):
                yield Belief(question.proposition)
            else:
                yield Belief(negate_proposition(question.proposition))


def is_relevant_answer(question, proposition, domain):
    if isinstance(proposition, Not):
        return is_relevant_answer(question, proposition.content, domain)
    if isinstance(question, BooleanQuestion):
        if isinstance(question.proposition, Not):
            return is_relevant_answer(BooleanQuestion(question.proposition.content), proposition, domain)
        if isinstance(question.proposition, Supports):
            return proposition == question.proposition or Not(question.proposition) == proposition
        if question.proposition.__class__ == proposition.__class__:
            return True
    if isinstance(question, WhQuestion):
        return isinstance(proposition, question.predicate)
    if isinstance(question, Why):
        if isinstance(question.explanandum, Not):
            return is_relevant_answer(Why(question.explanandum.content), proposition, domain)
        if depends(question.explanandum.__class__, proposition.__class__, domain):
            return True
        if isinstance(question.explanandum, Explains) and isinstance(proposition, Supports):
            explains = question.explanandum
            for supporting_proposition in domain.get_support(explains.explanandum):
                if supporting_proposition == explains.explanans:
                    return True


def depends(semantic_class, dependent_semantic_class, domain):
    if semantic_class in domain.dependencies:
        return dependent_semantic_class in domain.dependencies[semantic_class]


def select_explanations(explanandum, beliefs, domain):
    enthymematic_explanantia = list(get_enthymematic_explanantia(explanandum, beliefs, domain))
    if enthymematic_explanantia:
        return enthymematic_explanantia
    topos = get_topos(explanandum, domain)
    if topos:
        return [topos]
    return []


def get_enthymematic_explanantia(explanandum, beliefs, domain):
    for supporting_proposition in domain.get_support(explanandum):
        yield Belief(supporting_proposition)


def get_topos(explanandum, domain):
    if isinstance(explanandum, Explains):
        supporting_propositions = list(domain.get_support(explanandum.explanandum))
        if len(supporting_propositions) > 0:
            return Belief(Supports(supporting_propositions[0], explanandum.explanandum))


def confidence_to_hedge_level(confidence):
    if confidence is None:
        return None
    elif confidence >= 0.9:
        return strong
    elif confidence >= 0.1:
        return medium
    else:
        return weak
