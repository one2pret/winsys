from weekdaymasses.tests import *

class TestWhatsNewController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='whats_new'))
        # Test response...
