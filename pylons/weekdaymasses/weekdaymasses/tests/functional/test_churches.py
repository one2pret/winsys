from weekdaymasses.tests import *

class TestChurchesController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='churches'))
        # Test response...
