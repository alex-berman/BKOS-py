from bkos.semantics import *
from bkos.pragmatics import *
from bkos.logger import logger
from bkos.isu import try_rule


def get_latest_moves(state: DialogState):
    yield True
    state.private.non_integrated_moves = []
    state.shared.latest_moves = []
    if state.user_input and state.user_input.move:
        state.private.non_integrated_moves.append(state.user_input.move)
        state.shared.latest_moves.append(state.user_input.move)


def emit_move_on_agenda(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], EmitMove):
        yield True
        agenda_item = state.private.agenda.pop(0)
        state.next_system_move = agenda_item.move


def select_negative_understanding_icm(state: DialogState):
    if state.user_input and state.user_input.move is None:
        yield True
        state.next_system_move = ICM(level=understanding, polarity=negative)


def update_beliefs(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], Respond):
        yield True
        agenda_item = state.private.agenda[0]
        question = agenda_item.question
        beliefs = get_answers(question, state.private.beliefs, state.domain)
        question = state.private.agenda[0].question
        for belief in beliefs:
            logger.info('add answer to private beliefs', question=question, belief=belief)
            state.private.beliefs.append(belief)


def respond(state: DialogState):
    if len(state.private.agenda) > 0 and isinstance(state.private.agenda[0], Respond):
        agenda_item = state.private.agenda[0]
        excluded_propositions = state.shared.asserted if agenda_item.continuation else []
        question = agenda_item.question
        beliefs = [
            belief for belief in state.private.beliefs
            if is_relevant_answer(question, belief.proposition, state.domain) and \
                    belief.proposition not in excluded_propositions
        ]
        if len(beliefs) > 0 or agenda_item.continuation:
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
        question = agenda_item.question
        for belief in state.private.beliefs:
            if is_relevant_answer(question, belief.proposition, state.domain):
                return
        if len(list(get_answers(question, state.private.beliefs, state.domain))) == 0:
            yield True
            agenda_item = state.private.agenda.pop(0)
            question = agenda_item.question
            state.next_system_move = ICM(level=acceptance, polarity=negative, reason=LackKnowledge(question))


def integrate_user_ask(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, Ask):
            if not (isinstance(move.question, Why) and move.question.explanandum) or is_compatible_with_beliefs(
                    move.question.explanandum, state.private.beliefs, state.domain):
                yield True
                move = state.private.non_integrated_moves.pop(0)
                assert isinstance(move, Ask)
                resolved_question = resolve_elliptical_question(move.question, state) if is_elliptical_question(move.question) \
                    else move.question
                if resolved_question:
                    state.shared.qud.insert(0, resolved_question)
                    continuation = (isinstance(move.question, Why) and move.question.additional)
                    state.private.agenda.insert(0, Respond(resolved_question, continuation=continuation))
                else:
                    state.next_system_move = ICM(understanding, negative)


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
                        state.private.agenda.insert(0, Respond(resolved_question))
                        return
                implicit_question = Why(state.previous_system_move.proposition)
                state.shared.qud.insert(0, implicit_question)
                state.private.agenda.insert(0, Respond(implicit_question))


def acknowledge_user_assertion(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, Assert):
            yield True
            state.private.non_integrated_moves.pop(0)
            state.next_system_move = ICM(acceptance, positive)


def reject_question_with_incompatible_presupposition(state: DialogState):
    if len(state.private.non_integrated_moves) > 0:
        move = state.private.non_integrated_moves[0]
        if isinstance(move, Ask):
            if isinstance(move.question, Why) and move.question.explanandum is not None:
                if not is_compatible_with_beliefs(
                    move.question.explanandum, state.private.beliefs, state.domain):
                    yield True
                    move = state.private.non_integrated_moves.pop(0)
                    assert isinstance(move, Ask)
                    assert isinstance(move.question, Why)
                    state.next_system_move = ICM(
                        level=acceptance, polarity=negative, reason=move.question.explanandum)


def update_and_select(state: DialogState):
    logger.info('update_and_select', user_input=state.user_input)
    try_rule(state, get_latest_moves)
    try_rule(state, emit_move_on_agenda)
    try_rule(state, select_negative_understanding_icm)
    try_rule(state, integrate_user_ask)
    try_rule(state, integrate_user_negative_understanding)
    try_rule(state, acknowledge_user_assertion)
    try_rule(state, reject_question_with_incompatible_presupposition)
    try_rule(state, reject_unanswerable_question)
    try_rule(state, update_beliefs)
    try_rule(state, respond)
