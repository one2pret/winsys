import datetime
import logging

from weekdaymasses.lib.base import *
from weekdaymasses import model
from weekdaymasses.lib import utils

log = logging.getLogger(__name__)

class WhatsNewController(BaseController):

    areas = "masses", "whats_new"
    title = "What's New?"
    
    def __init__ (self):
      query = model.Session.query (model.WhatsNew).order_by ("updated_on")
      self.updates = {}
      for row in query:
        self.updates.setdefault (row.updated_on, []).append (row.linked_text ())
    
    def index (self, language):
      c.title = self.title
      c.areas = self.areas
      c.updates = self.updates
      return render ("/%s/whats_new.mako" % language)
