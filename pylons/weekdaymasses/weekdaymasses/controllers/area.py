import logging

from weekdaymasses.lib.base import *

log = logging.getLogger(__name__)

class AreaController (BaseController):

  areas = "masses", "area"
  
  def index (self):
    # Return a rendered template
    #   return render('/some/template.mako')
    # or, Return a response
    return 'Hello World'

  def churches (self, language, area_code, church_id):
    c.area = model.Area.get_by (code=area_code)
    c.title = "Churches in %s" % c.area.name
    c.churches = c.area.all_churches ()
    c.model = model
    c.areas = self.areas
    return render ("/%s/churches.mako" % language)
