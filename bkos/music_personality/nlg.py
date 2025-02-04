from bkos.music_personality.ontology import *
from bkos.music_personality.nl import feature_np
from bkos.music_personality.audio_features import AUDIO_FEATURES


extraversion_adjective = {
    False: 'introverted',
    True: 'extraverted',
}


audio_features_by_name = {
    feature['name']: feature
    for feature in AUDIO_FEATURES
}


def generate(move):
    clause = generate_clause(move)
    return initial_upper_case(clause)


def initial_upper_case(s):
    return s[:1].upper() + s[1:] if s else s


def generate_clause(move):
    if isinstance(move, OfferHelp):
        return 'How can I help?'
    if isinstance(move, Assert):
        return generate_assert_move(move.proposition, move.hedge)
    if isinstance(move, Confirm):
        return generate_boolean_constative('Yes', move.proposition, move.hedge)
    if isinstance(move, Disconfirm):
        return generate_boolean_constative('No', move.proposition, move.hedge)
    if isinstance(move, ICM):
        return generate_icm(move)
    raise Exception(f'Failed to generate clause for move {move}')


def generate_assert_move(proposition, hedge):
    if proposition in [Extraverted(), Not(Extraverted())]:
        return generate_extraversion_assertion(proposition, hedge)
    if isinstance(proposition, HighValue) or (
            isinstance(proposition, Not) and isinstance(proposition.content, HighValue)):
        return f"The person likes {generate_feature_value_judgement(proposition)}."
    if isinstance(proposition, HigherThanAverage) or (
            isinstance(proposition, Not) and isinstance(proposition.content, HigherThanAverage)):
        return generate_higher_than_average(proposition)
    if isinstance(proposition, Supports):
        return generate_supports(proposition)
    if isinstance(proposition, Not) and isinstance(proposition.content, Supports):
        return generate_not_supports(proposition.content)
    if isinstance(proposition, And):
        return generate_conjunction_proposition(proposition)
    raise Exception(f'Failed to generate assert move with proposition {proposition}')


def generate_boolean_constative(initial_confirmation_particle, proposition, hedge):
    main_clause = generate_assert_move(proposition, hedge)
    if isinstance(proposition, Supports) or (
            isinstance(proposition, Not) and isinstance(proposition.content, Supports)):
        return f'{initial_confirmation_particle}, {main_clause}'
    else:
        return main_clause


def generate_extraversion_assertion(proposition, hedge):
    adjective = generate_extraversion_adjective(proposition)
    if hedge == strong:
        return f"I'm quite confident that this person is {adjective}."
    elif hedge == medium:
        return f"I think this person is {adjective}."
    elif hedge == weak:
        return f"If I had to guess, I'd say that this person is {adjective}."


def generate_extraversion_adjective(proposition):
    positive = not isinstance(proposition, Not)
    return extraversion_adjective[positive]


def generate_feature_value_judgement(proposition):
    if isinstance(proposition, Not):
        label_name = 'negative_label'
        feature_name = proposition.content.feature.__name__
    else:
        label_name = 'positive_label'
        feature_name = proposition.feature.__name__
    return audio_features_by_name[feature_name][label_name]


def generate_supports(proposition):
    return f"statistically, people that like {generate_feature_value_judgement(proposition.antecedent)} are more likely to be {generate_extraversion_adjective(proposition.consequent)}."


def generate_not_explains(proposition):
    return f"no, statistically, people that like {generate_feature_value_judgement(proposition.explanans)} are not more likely to be {generate_extraversion_adjective(proposition.explanandum)}."


def generate_not_supports(proposition):
    return f"statistically, people that like {generate_feature_value_judgement(proposition.antecedent)} are not more likely to be {generate_extraversion_adjective(proposition.consequent)}."


def generate_higher_than_average(proposition):
    if isinstance(proposition, HigherThanAverage):
        return f'music heard by the person has a higher average score for {feature_np[proposition.feature.__name__]} than music in general.'
    elif isinstance(proposition, Not) and isinstance(proposition.content, HigherThanAverage):
        return f'music heard by the person has a lower average score for {feature_np[proposition.content.feature.__name__]} than music in general.'



def generate_icm(move):
    if move.level == acceptance:
        if move.polarity == positive:
            return 'OK.'
        if move.polarity == negative:
            return generate_negative_acceptance(move.reason)
    if move.level == understanding and move.polarity == negative:
        return "Sorry, I don't understand."
    raise Exception(f'Failed to generate ICM move {move}')


def generate_negative_acceptance(reason):
    if isinstance(reason, LackKnowledge):
        if isinstance(reason.question, Why) and isinstance(reason.question.explanandum, Supports) and \
                reason.question.explanandum.consequent in [Extraverted(), Not(Extraverted())]:
            return "I cannot explain the reason behind the correlations that I've found."
        raise Exception(f'Failed to generate negative acceptance ICM with reason {reason}')
    if reason in [Extraverted(), Not(Extraverted())]:
        return f"No, I don't think this person is {generate_extraversion_adjective(reason)}."
    if isinstance(reason, HighValue) or (isinstance(reason, Not) and isinstance(reason.content, HighValue)):
        return f"No, I don't think this person likes {generate_feature_value_judgement(reason)}."
    if isinstance(reason, Explains):
        return generate_not_explains(reason)
    if isinstance(reason, NoAdditionalAnswers):
        if isinstance(reason.question, Why):
            explanandum = reason.question.explanandum
            if explanandum in [Extraverted(), Not(Extraverted())]:
                return f"I don't see any other reasons to believe that the person is {generate_extraversion_adjective(explanandum)}."
    raise Exception(f'Failed to generate negative acceptance ICM for reason {reason}')


def generate_conjunction_proposition(proposition):
    if all([isinstance(conjunct, FactorConsidered) for conjunct in proposition.conjuncts]):
        terms = [feature_np[conjunct.factor.__name__] for conjunct in proposition.conjuncts]
        return f'I consider music heard by the person in terms of the following audio features: {generate_conjunction(terms)}.'
    else:
        raise Exception(f'Failed to generate conjunction for proposition {proposition}')


def generate_conjunction(terms):
    if len(terms) == 1:
        return terms[0]
    elif len(terms) == 2:
        return f'{terms[0]} and {terms[1]}'
    elif len(terms) > 1:
        return f'{terms[0]}, {generate_conjunction(terms[1:])}'
