import yaml
import pytest
from pathlib import Path

from bkos import bot
import bkos.hello_world.domain
import bkos.hello_world.nlu
import bkos.hello_world.nlg
from bkos.test.dialogtest import run_dialog_test_nl


test_contents = yaml.load(open(f'{Path(__file__).parent}/dialog_coverage_nl.yml').read(), yaml.Loader)


class TestDialogs(object):
    @pytest.mark.parametrize('name,content', test_contents.items())
    def test_dialog(self, name, content):
        resources = {
            'domain_class': bkos.hello_world.domain.HelloWorldDomain,
            'nlu': bkos.hello_world.nlu,
            'nlg': bkos.hello_world.nlg,
        }
        run_dialog_test_nl(bot, resources, content['turns'])
