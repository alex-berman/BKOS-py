from typing import Callable, Any
from types import GeneratorType

from bkos.ontology import DialogState
from bkos.logger import logger


Rule = Callable[[DialogState], Any]


def try_rule(state: DialogState, rule: Rule):
    logger.debug('try_rule', rule=rule.__name__, state=state)
    result = rule(state)
    if result:
        if isinstance(result, GeneratorType):
            def get_first_item():
                for item in result:
                    return item

            conditional = get_first_item()
            if conditional:
                logger.info('preconditions true', rule=rule.__name__)

                def apply_effects():
                    try:
                        next(result)
                    except StopIteration:
                        pass

                apply_effects()
                return True
