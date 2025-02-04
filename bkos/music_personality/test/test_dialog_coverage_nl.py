from unittest.mock import MagicMock
import yaml

import pytest

from bkos import bot
import bkos.music_personality.domain
import bkos.music_personality.nlu_simple
import bkos.music_personality.nlg
from bkos.test.dialogtest import run_dialog_test_nl


game_modes = {
    False: 'normal_mode',
    True: 'game_mode',
}


def load_tests():
    for game_mode in game_modes.keys():
        contents = yaml.load(
            open(f'bkos/music_personality/test/dialog_coverage_{game_modes[game_mode]}_nl.yml').read(), yaml.Loader)
        for name, content in contents.items():
            yield game_mode, name, content


class TestDialogs(object):
    @pytest.mark.parametrize('game_mode, name, content', load_tests())
    def test_dialog(self, game_mode, name, content):
        resources = {
            'game_mode': game_mode,
            'domain_class': bkos.music_personality.domain.MusicPersonalityDomain,
            'nlu': bkos.music_personality.nlu_simple,
            'nlg': bkos.music_personality.nlg,
        }
        resources['extraversion_model_bundle'] = {
            'model': MagicMock(),
            'scaler': MagicMock(),
        }
        resources['explainer'] = MagicMock()
        session_data = {'case_info': {}}
        facts = content['facts'] if 'facts' in content else {}
        if 'feature_values' in facts:
            session_data['case_info']['feature_values'] = facts['feature_values']
            resources['extraversion_model_bundle']['features'] = facts['feature_values'].keys()
        if 'predicted_extraversion_prob' in facts:
            p = facts['predicted_extraversion_prob']
            resources['extraversion_model_bundle']['model'].predict_proba.return_value = [[p, 1 - p]]
        if 'global_coefficients' in facts:
            resources['explainer'].global_coefficients.return_value = facts['global_coefficients']
        if 'local_contributions' in facts:
            resources['explainer'].local_contributions.return_value = facts['local_contributions']
        run_dialog_test_nl(bot, resources, content['turns'], session_data)
