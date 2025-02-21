from unittest.mock import MagicMock

import bkos.music_personality.domain
import bkos.music_personality.nlu_simple
import bkos.music_personality.nlg


resources = {
    'game_mode': False,
    'domain_class': bkos.music_personality.domain.MusicPersonalityDomain,
    'nlu': bkos.music_personality.nlu_simple,
    'nlg': bkos.music_personality.nlg,
    'extraversion_model_bundle': {
        'model': MagicMock(),
        'scaler': MagicMock(),
        'features': ['energy_mean', 'danceability_mean', 'valence_mean', 'loudness_mean']
    },
    'explainer': MagicMock(),
}

resources['extraversion_model_bundle']['model'].predict_proba.return_value = [[0.4, 0.6]]
resources['explainer'].global_coefficients.return_value = {
    'energy_mean': -0.2,
    'danceability_mean': 2,
    'valence_mean': 0.5,
    'loudness_mean': -1,
}
resources['explainer'].local_contributions.return_value = {
    'energy_mean': -0.1,
    'danceability_mean': -0.2,
    'valence_mean': -0.05,
    'loudness_mean': 0.1
}

session_data = {
    'case_info': {
        'feature_values': {
            'energy_mean': 0.5,
            'danceability_mean': -0.1,
            'valence_mean': -0.1,
            'loudness_mean': 0.2
        }

    }
}