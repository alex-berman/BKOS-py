from music_personality import ontology
from music_personality.ontology import *
from music_personality.audio_features import AUDIO_FEATURES


def interpret(utterance_cased):
    utterance = utterance_cased.lower()
    tokens = utterance.rstrip('.?!').split(' ')

    def detect_extraversion_proposition():
        if 'introverted' in tokens:
            return Not(Extraverted())
        if 'extraverted' in tokens:
            return Extraverted()

    def detect_feature_value_judgement_proposition():
        def get_score_for_substring_match(string, substring):
            if substring in string:
                return len(substring)

        def get_scored_interpretations():
            for feature in AUDIO_FEATURES:
                score = get_score_for_substring_match(utterance, feature['positive_label'])
                if score:
                    yield HighValue(getattr(ontology, feature['name'])), score
                score = get_score_for_substring_match(utterance, feature['negative_label'])
                if score:
                    yield Not(HighValue(getattr(ontology, feature['name']))), score

        scored_interpretations = list(get_scored_interpretations())
        if len(scored_interpretations) > 0:
            best_scored_interpretation = max(
                scored_interpretations, key=lambda scored_interpretation: scored_interpretation[1])
            return best_scored_interpretation[0]

    def try_interpret_as_why_question_concerning_explanation():
        extraversion_proposition = detect_extraversion_proposition()
        if extraversion_proposition:
            feature_value_judgement_proposition = detect_feature_value_judgement_proposition()
            if feature_value_judgement_proposition:
                return Ask(Why(Explains(feature_value_judgement_proposition, extraversion_proposition)))

    extraversion_proposition = detect_extraversion_proposition()
    feature_value_judgement_proposition = detect_feature_value_judgement_proposition()
    additional_reasons = ('other' in tokens and ('reason' in tokens or 'reasons' in tokens))

    if 'why' in tokens:
        if extraversion_proposition:
            return Ask(Why(extraversion_proposition, additional=additional_reasons))
        if feature_value_judgement_proposition:
            return Ask(Why(feature_value_judgement_proposition))
        return Ask(Why(additional=additional_reasons))
    if 'how' in tokens and 'explain' in tokens:
        move = try_interpret_as_why_question_concerning_explanation()
        if move:
            return move
    if "don't understand" in utterance or 'so what' in utterance:
        return ICM(understanding, negative)
    if 'support' in tokens:
        if extraversion_proposition and feature_value_judgement_proposition:
                return Ask(BooleanQuestion(Supports(feature_value_judgement_proposition, extraversion_proposition)))
    if 'think' in tokens and 'you' in tokens and extraversion_proposition:
        return Ask(BooleanQuestion(extraversion_proposition))
    if 'think' in tokens and 'i' in tokens and extraversion_proposition:
        return Assert(extraversion_proposition)
    if 'which factors' in utterance:
        return Ask(WhQuestion(FactorConsidered))
    if utterance == 'ok':
        return ICM(acceptance, positive)
    if additional_reasons:
        return Ask(Why(explanandum=None, additional=True))
