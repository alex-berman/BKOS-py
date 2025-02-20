import bkos.hello_world.domain
import bkos.hello_world.nlu
import bkos.hello_world.nlg


resources = {
    'domain_class': bkos.hello_world.domain.HelloWorldDomain,
    'nlu': bkos.hello_world.nlu,
    'nlg': bkos.hello_world.nlg,
}

session_data = None
