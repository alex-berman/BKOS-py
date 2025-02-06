import yaml

import pytest

from bkos import bot
import hello_world.domain
import hello_world.nlu
import hello_world.nlg
from bkos.test.dialogtest import run_dialog_test_nl


test_contents = yaml.load(open('hello_world/test/dialog_coverage_nl.yml').read(), yaml.Loader)


class TestDialogs(object):
    @pytest.mark.parametrize('name,content', test_contents.items())
    def test_dialog(self, name, content):
        resources = {
            'domain_class': hello_world.domain.DemoDomain,
            'nlu': hello_world.nlu,
            'nlg': hello_world.nlg,
        }
        run_dialog_test_nl(bot, resources, content['turns'])
