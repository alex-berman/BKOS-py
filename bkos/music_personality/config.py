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
        'features': MagicMock(),
    },
    'explainer': MagicMock(),
}

session_data = {
    'case_info': {

    }
}