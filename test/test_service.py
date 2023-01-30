from nameko.testing.services import worker_factory

from temp_messenger.service import BasicService


#
# In order to run the tests we need to run in the command line:
# $ pytest
#


def test_method():
    service = worker_factory(BasicService)
    result = service.basic_method()
    assert result == 'Hello, world!'
