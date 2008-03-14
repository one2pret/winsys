from weekdaymasses.tests import *

class TestAreaController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='area'))
        # Test response...
