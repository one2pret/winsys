import logging

from weekdaymasses.lib.base import *
from weekdaymasses.lib import utils

log = logging.getLogger(__name__)

class RootController(BaseController):

  languages = [u"en", u"es"]
  default_language = languages[0]

  def index(self, language=None):
    if language is None:
      languages = utils.preferred_languages (request.environ.get ("HTTP_ACCEPT_LANGUAGE", self.default_language))
      for language in languages:
        lang, sub = (language + "-").split ("-")[:2]
        if language in self.languages:
          redirect_to (h.url_for (controller="root", language=language))
        elif lang in self.languages:
          redirect_to (h.url_for (controller="root", language=lang))
      else:
        redirect_to (h.url_for (controller="root", language=self.default_language))
    else:
      c.title = "weekdaymasses.org.uk"
      c.areas = ["index"]
      return render ("/%s/index.mako" % language)
