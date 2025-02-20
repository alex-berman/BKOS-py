import yaml
import pytest
from pathlib import Path

from bkos import bot
import bkos.hello_world.config
from bkos.test.dialogtest import run_dialog_test_nl


test_contents = yaml.load(open(f'{Path(__file__).parent}/dialog_coverage_nl.yml').read(), yaml.Loader)


class TestDialogs(object):
    @pytest.mark.parametrize('name,content', test_contents.items())
    def test_dialog(self, name, content):
        run_dialog_test_nl(bot, bkos.hello_world.config.resources, content['turns'])
