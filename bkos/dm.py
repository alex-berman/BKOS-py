from bkos.semantics import *
from bkos.pragmatics import *
from bkos.logger import logger
from bkos.isu import try_rule


def get_latest_moves(state: DialogState):
    yield True
    state.private.non_integrated_moves = []
    state.private.non_integrated_goals = []
    if state.user_input and state.user_input.move:
        state.private.non_integrated_moves.append(state.user_input.move)


def integrate_continuation_request(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, RequestContinuation) and isinstance(move.content, Ask):
            yield True
            state.private.non_integrated_moves.pop(0)
            state.private.non_integrated_goals.append(Goal(move.content.question, continuation=True))


def integrate_user_ask(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, Ask):
            yield True
            state.private.non_integrated_moves.pop(0)
            state.private.non_integrated_goals.append(Goal(move.question))


def emit_move_on_agenda(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], EmitMove):
        yield True
        agenda_item = state.private.agenda.pop(0)
        state.next_system_move = agenda_item.move


def select_negative_understanding_icm(state: DialogState):
    if state.user_input and (
            state.user_input.move is None or
            len(state.private.non_integrated_moves) > 0 or
            len(state.private.non_integrated_goals) > 0):
        yield True
        state.next_system_move = ICM(level=understanding, polarity=negative)


def update_beliefs(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], Respond):
        yield True
        agenda_item = state.private.agenda[0]
        question = agenda_item.goal.question
        beliefs = get_answers(question, state.private.beliefs, state.domain)
        question = state.private.agenda[0].goal.question
        for belief in beliefs:
            logger.info('add answer to private beliefs', question=question, belief=belief)
            state.private.beliefs.append(belief)


def respond(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], Respond):
        agenda_item = state.private.agenda[0]
        goal = agenda_item.goal
        excluded_propositions = state.shared.asserted if goal.continuation else []
        question = goal.question
        beliefs = [
            belief for belief in state.private.beliefs
            if is_relevant_answer(question, belief.proposition, state.domain) and \
                    belief.proposition not in excluded_propositions
        ]
        if len(beliefs) > 0 or goal.continuation:
            yield True
            state.private.agenda.pop(0)
            if len(beliefs) == 0:
                state.next_system_move = ICM(acceptance, negative, NoAdditionalAnswers(question))
            else:
                if isinstance(question, BooleanQuestion):
                    assert len(beliefs) == 1
                    belief = beliefs[0]
                    hedge = confidence_to_hedge_level(belief.confidence)
                    if question.proposition == belief.proposition:
                        move = Confirm(belief.proposition, hedge)
                    else:
                        move = Disconfirm(belief.proposition, hedge)
                else:
                    delivery_strategy = state.domain.answer_delivery_strategy(question)
                    if delivery_strategy == AnswerDeliveryStrategy.INCREMENTAL:
                        belief = beliefs[0]
                        hedge = confidence_to_hedge_level(belief.confidence)
                    else:
                        belief = Belief(And([belief.proposition for belief in beliefs]))
                        hedges = set([
                            confidence_to_hedge_level(belief.confidence)
                            for belief in beliefs
                        ])
                        assert len(hedges) == 1
                        hedge = list(hedges)[0]
                    move = Assert(belief.proposition, hedge)
                state.next_system_move = move
                state.shared.asserted.append(belief.proposition)
                logger.debug(f'selected {state.next_system_move} as answer to {question} based on belief {belief}')


def reject_unanswerable_question(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], Respond):
        agenda_item = state.private.agenda[0]
        question = agenda_item.goal.question
        for belief in state.private.beliefs:
            if is_relevant_answer(question, belief.proposition, state.domain):
                return
        if len(list(get_answers(question, state.private.beliefs, state.domain))) == 0:
            yield True
            state.private.agenda.pop(0)
            state.next_system_move = ICM(level=acceptance, polarity=negative, reason=LackKnowledge(question))


def integrate_question_goal(state: DialogState):
    if len(state.private.non_integrated_goals) > 0:
        goal = state.private.non_integrated_goals[0]
        question = goal.question
        if not (isinstance(question, Why) and question.explanandum) or is_compatible_with_beliefs(
                question.explanandum, state.private.beliefs, state.domain):
            resolved_question = resolve_elliptical_question(goal, state) if is_elliptical_question(question) \
                else question
            if resolved_question:
                yield True
                state.private.non_integrated_goals.pop(0)
                state.shared.qud.insert(0, resolved_question)
                state.private.agenda.insert(0, Respond(Goal(resolved_question, goal.continuation)))


def integrate_user_negative_understanding(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, ICM) and move.level == understanding and move.polarity == negative:
            yield True
            state.private.non_integrated_moves.pop(0)
            if isinstance(state.previous_system_move, Constative):
                if len(state.shared.qud) > 0:
                    topmost_qud = state.shared.qud[0]
                    if isinstance(topmost_qud, Why):
                        resolved_question = Why(Explains(state.previous_system_move.proposition, topmost_qud.explanandum))
                        state.shared.qud.insert(0, resolved_question)
                        state.private.agenda.insert(0, Respond(Goal(resolved_question)))
                        return
                implicit_question = Why(state.previous_system_move.proposition)
                state.shared.qud.insert(0, implicit_question)
                state.private.agenda.insert(0, Respond(Goal(implicit_question)))


def integrate_user_positive_acceptance(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, ICM) and move.level == acceptance and move.polarity == positive:
            yield True
            state.private.non_integrated_moves.pop(0)


def acknowledge_user_assertion(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, Assert):
            yield True
            state.private.non_integrated_moves.pop(0)
            state.next_system_move = ICM(acceptance, positive)


def reject_question_with_incompatible_presupposition(state: DialogState):
    if len(state.private.non_integrated_goals) > 0:
        question = state.private.non_integrated_goals[0].question
        if isinstance(question, Why) and question.explanandum is not None:
            if not is_compatible_with_beliefs(question.explanandum, state.private.beliefs, state.domain):
                yield True
                state.private.non_integrated_goals.pop(0)
                state.next_system_move = ICM(level=acceptance, polarity=negative, reason=question.explanandum)


def update_and_select(state: DialogState):
    logger.info('update_and_select', user_input=state.user_input)
    try_rule(state, get_latest_moves)
    try_rule(state, integrate_continuation_request)
    try_rule(state, integrate_user_ask)
    try_rule(state, emit_move_on_agenda)
    try_rule(state, integrate_question_goal)
    try_rule(state, integrate_user_negative_understanding)
    try_rule(state, integrate_user_positive_acceptance)
    try_rule(state, acknowledge_user_assertion)
    try_rule(state, reject_question_with_incompatible_presupposition)
    try_rule(state, reject_unanswerable_question)
    try_rule(state, update_beliefs)
    try_rule(state, respond)
    try_rule(state, select_negative_understanding_icm)
