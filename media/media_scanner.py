import os, sys

from path import path
from pyglet import media

import ini

class Media (object):
  
  FAIL, NA, WARNING, PASS = -1, 0, 1, 2
  
  def __init__ (self, filepath):
    self.filepath = filepath
    self.media = media.load (filepath)
    
  @classmethod
  def _assert (cls, media_value, reference_value):
    if truth_value:
      return cls.PASS, media_value
    else:
      return cls.FAIL, media_value
  
  def screen_resolution (self, value):
    value = [int (i) for i in value.split ("x")]
    if self.media.video_format:
      if self.media.video_format.width & self.media.video_format.height:
        media_value = [self.media.video_format.width, self.media.video_format.height]
        if media_value == value:
          return self.PASS, media_value
        elif set (media_value) == set (value):
          return self.WARNING, media_value
        else:
          return self.FAIL, media_value
    else:
      return self.NA, None

  def aspect_ratio (self, value):
    if self.media.video_format:
      if value == self.media.video_format.display_aspect_ratio:
        return self.PASS, self.media.video_format.display_aspect_ratio
      elif set (value) == set (self.media.video_format.display_aspect_ratio):
        return self.WARNING, self.media.video_format.display_aspect_ratio
      else:
        return self.FAIL, self.media.video_format.display_aspect_ratio
    else:
      return self.NA, None
      
  def video_format (self, value):
    if self.media.video_format:
      return self._assert (self.media.video_format.codec_name.lower () == value.lower ())
    else:
      return self.NA
      
  def frame_rate (self, value):
    if self.media.video_format:
      return self._assert (self.media.video_format.frame_rate == value)
    else:
      return self.NA
      
  def audio_sample_bits (self, value):
    if self.media.audio_format:
      return self._assert (self.media.audio_format.sample_bits == value)
    else:
      return self.NA
      
  def multiplex_bit_rate (self, value):
    if self.media.duration <> 0:
      return self._assert (8 * self.filepath.size / self.media.duration == value)
    else:
      return self.NA
      
  def video_bit_rate (self, value):
    if self.media.video_format:
      return self._assert (self.media.video_format.bit_rate == value)
    else:
      return self.NA
      
  def audio_bit_rate (self, value):
    if self.media.audio_format:
      return self._assert (self.media.audio_format.bit_rate == value)
    else:
      return self.NA
      
  def audio_codec (self, value):
    if self.media.audio_format:
      return self._assert (self.media.audio_format.codec_name == value)
    else:
      return self.NA
      
  def audio_sample_rate (self, value):
    if self.media.audio_format:
      return self._assert (self.media.audio_format.sample_rate == value)
    else:
      return self.NA
      
  def n_channels (self, value):
    if self.media.audio_format:
      return self._assert (self.media.audio_format.channels == value)
    else:
      return self.NA

CHECK_BOTH_WAYS = ['']
def check_file (media_type, filepath, options):
  print
  print filepath
  media_file = Media (filepath)
  for name, value in options.items ():
    print "  ", name, "=>",
    if hasattr (media_file, name):
      result = getattr (media_file, name) (value)
      if result == Media.PASS:
        print "Success"
      elif result == Media.FAIL:
        print "Failure"
      elif result == Media.NA:
        print "Unable to determine result"
      else:
        raise RuntimeError, "Unexpected result from check"
    else:
      print "NA"

EXTENSIONS = ("wmv", "mpg")
def main (args):
  scanner_ini = ini.Ini ("media_scanner.ini")
  media_types = scanner_ini.sections ()
  
  if len (args) >= 2:
    media_type = args[1].lower ()
  else:
    media_type = raw_input ("Media type (%s): " % (", ".join (media_types)))
  options = dict (list (getattr (scanner_ini, media_type)))
    
  if len (args) >= 1:
    filepath = path (args[0])
  else:
    filepath = path (raw_input ("File / folder: "))

  if filepath.isfile ():
    check_file (media_type, filepath, options)
  else:
    for media_filepath in filepath.walk ():
      if media_filepath.endswith (EXTENSIONS):
        check_file(media_type, media_filepath, options)
  
if __name__ == '__main__':
  main (sys.argv[1:])    
  raw_input ("Press enter...")
