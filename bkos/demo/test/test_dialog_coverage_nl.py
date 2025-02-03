from unittest.mock import MagicMock
import yaml

import pytest

from bkos import bot
import bkos.demo.domain
import bkos.demo.nlu
import bkos.demo.nlg
from bkos.test.dialogtest import run_dialog_test_nl


test_contents = yaml.load(open('bkos/demo/test/dialog_coverage_nl.yml').read(), yaml.Loader)


class TestDialogs(object):
    @pytest.mark.parametrize('name,content', test_contents.items())
    def test_dialog(self, name, content):
        resources = {
            'domain_class': bkos.demo.domain.DemoDomain,
            'nlu': bkos.demo.nlu,
            'nlg': bkos.demo.nlg,
        }
        run_dialog_test_nl(bot, resources, content['turns'])
