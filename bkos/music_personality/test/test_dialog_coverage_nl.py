from unittest.mock import MagicMock

import yaml
import pytest
from pathlib import Path

from bkos import bot
import bkos.music_personality.config
from bkos.test.dialogtest import run_dialog_test_nl


def load_tests():
    contents = yaml.load(
        open(f'{Path(__file__).parent}/dialog_coverage_nl.yml').read(), yaml.Loader)
    for name, content in contents.items():
        yield name, content


class TestDialogs(object):
    @pytest.mark.parametrize('name, content', load_tests())
    def test_dialog(self, name, content):
        resources = bkos.music_personality.config.resources
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
