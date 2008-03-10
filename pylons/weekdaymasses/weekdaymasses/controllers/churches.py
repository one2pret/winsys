import logging

from weekdaymasses.lib.base import *

log = logging.getLogger(__name__)

class ChurchesController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return render ("/churches.mako")
