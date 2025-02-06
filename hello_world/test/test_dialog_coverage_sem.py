import yaml

import pytest

from bkos import bot
import hello_world
from bkos.test.dialogtest import run_dialog_test_sem
from bkos import semantic_serialization


test_contents = yaml.load(open('hello_world/test/dialog_coverage_sem.yml').read(), yaml.Loader)


class TestDialogs(object):
    @pytest.mark.parametrize('name,content', test_contents.items())
    def test_dialog(self, name, content):
        resources = {
            'domain_class': hello_world.domain.DemoDomain,
        }
        semantic_serialization.initialize()
        semantic_serialization.register_module(hello_world.ontology)
        run_dialog_test_sem(bot, resources, content['turns'])
