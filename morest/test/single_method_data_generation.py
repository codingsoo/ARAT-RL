import os
import logging

from prance import ResolvingParser

from build_graph import parse
from fuzzer.fuzzer import APIFuzzer
from fuzzer.normal_test_data_generator import RandomDataGenerator

logger = logging.getLogger('morest.test')


def default_reclimit_handler(limit, parsed_url, recursions=()):
    """Raise prance.util.url.ResolutionError."""
    return {
        "type": "object",
        "name": "Recursive Dependency",
        "properties": {}
    }


def main():
    parser = ResolvingParser("./debug_doc/spree.yaml",
                             backend='openapi-spec-validator', recursion_limit_handler=default_reclimit_handler)
    apis, odg = parse(parser.specification)
    for method in odg.nodes:
        for parameter_name in method.request_parameters:
            parameter = method.request_parameters[parameter_name]
            random_data_generator = RandomDataGenerator(parameter)
            result = random_data_generator.generate()
            logger.debug('Result: %s', result)
            if method.request_body is not None:
                generator = RandomDataGenerator(method.request_body)
                generated_value = generator.generate()
                data = generated_value
                logger.debug('Data: %s', data)


if __name__ == '__main__':
    main()
