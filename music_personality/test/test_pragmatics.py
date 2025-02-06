from unittest.mock import MagicMock

import pytest

from bkos.pragmatics import is_relevant_answer
import music_personality
from music_personality.ontology import *


class TestPragmatics(object):
    @pytest.mark.parametrize('question,proposition,return_value', [
        (BooleanQuestion(Extraverted()), Extraverted(), True),
        (BooleanQuestion(Extraverted()), Not(Extraverted()), True),
        (BooleanQuestion(Not(Extraverted())), Extraverted(), True),
        (BooleanQuestion(Not(Extraverted())), Not(Extraverted()), True),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Extraverted())), Extraverted(), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Extraverted())), HighValue(energy_mean), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Extraverted())), Not(Extraverted()), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Extraverted())),
         Not(Supports(Not(HighValue(danceability_mean)), Extraverted())), True),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Extraverted())),
         Supports(Not(HighValue(danceability_mean)), Extraverted()), True),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Not(Extraverted()))), Extraverted(), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Not(Extraverted()))), HighValue(energy_mean),
         False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Not(Extraverted()))), Not(Extraverted()), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Not(Extraverted()))),
         Not(Supports(Not(HighValue(danceability_mean)), Extraverted())), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Not(Extraverted()))),
         Supports(Not(HighValue(danceability_mean)), Extraverted()), False),
        (BooleanQuestion(Supports(Not(HighValue(danceability_mean)), Not(Extraverted()))),
         Supports(Not(HighValue(danceability_mean)), Not(Extraverted())), True),
        (WhQuestion(FactorConsidered), Extraverted(), False),
        (WhQuestion(FactorConsidered), FactorConsidered(energy_mean), True),
        (WhQuestion(FactorConsidered), Not(Extraverted()), False),
        (Why(Explains(HighValue(danceability_mean), Extraverted())), Extraverted(), False),
        (Why(Explains(HighValue(danceability_mean), Extraverted())), HighValue(danceability_mean), False),
        (Why(Explains(HighValue(energy_mean), Not(Extraverted()))), Extraverted(), False),
        (Why(Explains(HighValue(energy_mean), Not(Extraverted()))), HighValue(energy_mean), False),
        (Why(Explains(HighValue(energy_mean), Not(Extraverted()))), Not(Extraverted()), False),
        (Why(Explains(Not(HighValue(danceability_mean)), Not(Extraverted()))), Extraverted(), False),
        (
                Why(Explains(Not(HighValue(danceability_mean)), Not(Extraverted()))),
                HighValue(danceability_mean),
                False),
        (Why(Explains(Not(HighValue(danceability_mean)), Not(Extraverted()))), Not(Extraverted()), False),
        (Why(Explains(Not(HighValue(danceability_mean)), Not(Extraverted()))),
         Not(HighValue(danceability_mean)), False),
        (Why(Explains(Not(HighValue(energy_mean)), Extraverted())), Extraverted(), False),
        (Why(Explains(Not(HighValue(energy_mean)), Extraverted())), HighValue(energy_mean), False),
        (Why(Explains(Not(HighValue(energy_mean)), Extraverted())), Not(HighValue(energy_mean)), False),
        (Why(Extraverted()), Extraverted(), False),
        (Why(Extraverted()), HighValue(danceability_mean), True),
        (Why(Extraverted()), HighValue(energy_mean), True),
        (Why(Extraverted()), Not(HighValue(energy_mean)), True),
        (Why(HighValue(danceability_mean)), Extraverted(), False),
        (Why(HighValue(danceability_mean)), HighValue(danceability_mean), False),
        (Why(HighValue(danceability_mean)), HigherThanAverage(danceability_mean), True),
        (Why(Not(Extraverted())), Extraverted(), False),
        (Why(Not(Extraverted())), HighValue(danceability_mean), True),
        (Why(Not(Extraverted())), HighValue(energy_mean), True),
        (Why(Not(Extraverted())), Not(Extraverted()), False),
        (Why(Not(Extraverted())), Not(HighValue(danceability_mean)), True),
        (Why(Not(HighValue(danceability_mean))), Extraverted(), False),
        (Why(Not(HighValue(danceability_mean))), HighValue(danceability_mean), False),
        (Why(Not(HighValue(danceability_mean))), HigherThanAverage(danceability_mean), True),
        (Why(Not(HighValue(danceability_mean))), Not(Extraverted()), False),
        (Why(Not(HighValue(danceability_mean))), Not(HighValue(danceability_mean)), False),
        (Why(Not(HighValue(danceability_mean))), Not(HigherThanAverage(danceability_mean)), True),
    ])
    def test_is_relevant_answer(self, question, proposition, return_value):
        resources = {
            'game_mode': MagicMock(),
            'domain_class': music_personality.domain.MusicPersonalityDomain,
        }
        resources['extraversion_model_bundle'] = {
            'model': MagicMock(),
            'scaler': MagicMock(),
            'features': MagicMock(),
        }
        resources['explainer'] = MagicMock()
        session_data = {'case_info': {}}
        domain = music_personality.domain.MusicPersonalityDomain(resources, session_data)
        assert bool(is_relevant_answer(question, proposition, domain)) == return_value
