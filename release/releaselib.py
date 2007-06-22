import os, sys
import ConfigParser

class ReleaseConfig (object):

  def __init__ (self, filename):
    self.ini_filename = filename
    self.ini = ConfigParser.ConfigParser ()
    self.ini.read (filename)

    if self.ini.has_section ("files"):
      self.filenames = [self.ini.get ("files", i) for i in self.ini.options ("files")]
    else:
      self.filenames = []
