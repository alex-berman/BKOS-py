from typing import List

from bkos.domain import Domain
from bkos.music_personality import ontology
from bkos.music_personality.ontology import *


class MusicPersonalityDomain(Domain):
    def __init__(self, resources, session_data):
        self._game_mode = resources['game_mode']
        self._case_info = session_data['case_info']
        self._model = resources['extraversion_model_bundle']['model']
        self._scaler = resources['extraversion_model_bundle']['scaler']
        self._features = resources['extraversion_model_bundle']['features']
        self._explainer = resources['explainer']

    def initial_agenda(self) -> List[AgendaItem]:
        return [Respond(BooleanQuestion(Extraverted()))] if self._game_mode else [EmitMove(OfferHelp())]

    def initial_beliefs(self) -> List[Belief]:
        factors_considered = [
            energy_mean,
            mode_0_percentage,
            loudness_mean,
            speechiness_mean,
            instrumentalness_mean,
            valence_mean,
            danceability_mean,
        ]
        return ([Belief(FactorConsidered(audio_feature)) for audio_feature in factors_considered] +
                [self.get_extraversion_belief(self.featurize())])

    dependencies = {
        Extraverted: {HighValue},
        HighValue: {HigherThanAverage}
    }

    def featurize(self):
        feature_value_dict = self._case_info['feature_values']
        unscaled_feature_vector = [
            feature_value_dict[feature_name]
            for feature_name in self._features
        ]
        return self._scaler.transform([unscaled_feature_vector])[0]

    def get_extraversion_belief(self, feature_vector):
        extraversion_prob = self._model.predict_proba([feature_vector])[0][0]
        if extraversion_prob > .5:
            proposition = Extraverted()
            confidence = (extraversion_prob - .5) * 2
        else:
            proposition = Not(Extraverted())
            confidence = (.5 - extraversion_prob) * 2
        return Belief(proposition, confidence)

    def get_support(self, proposition):
        def get_support_for_prediction(extraverted):
            feature_vector = self.featurize()
            local_contributions = self._explainer.local_contributions(self._model, self._features, feature_vector)
            filter_function = lambda feature_name: (local_contributions[feature_name] > 0 if extraverted == 1
                                                    else local_contributions[feature_name] < 0)
            filtered_contributions = [
                feature_name for feature_name in local_contributions.keys()
                if filter_function(feature_name)]
            comparison_function = lambda feature_name: (-local_contributions[feature_name] if extraverted == 1
                                                        else local_contributions[feature_name])
            features_ranked_by_contribution = sorted(filtered_contributions, key=comparison_function)
            for feature_name in features_ranked_by_contribution:
                coefficient = self._explainer.global_coefficients(self._model, self._features)[feature_name]
                positive = True if (coefficient > 0 and extraverted == 1) or (
                        coefficient <= 0 and extraverted == 0) else False
                positive_proposition = HighValue(getattr(ontology, feature_name))
                yield positive_proposition if positive else Not(positive_proposition)

        if proposition == Extraverted():
            for supporting_proposition in get_support_for_prediction(1):
                yield supporting_proposition
        elif proposition == Not(Extraverted()):
            for supporting_proposition in get_support_for_prediction(0):
                yield supporting_proposition
        elif isinstance(proposition, HighValue):
            yield HigherThanAverage(proposition.feature)
        elif isinstance(proposition, Not) and isinstance(proposition.content, HighValue):
            yield Not(HigherThanAverage(proposition.content.feature))

    def answer_delivery_strategy(self, question) -> AnswerDeliveryStrategy:
        return AnswerDeliveryStrategy.INCREMENTAL if isinstance(question, Why) \
            else AnswerDeliveryStrategy.SINGLE_TURN
