import os, sys

from path import path
import media
#~ from pyglet import media
#~ from pyglet.media.drivers import openal

import ini

OPTIONS = [
  "duration",
  "screen_resolution",
  "aspect_ratio",
  "pixel_aspect_ratio",
  "video_format",
  "video_sample_bits",
  "audio_sample_bits",
  "frame_rate",
  "multiplex_bit_rate",
  "video_bit_rate",
  "audio_bit_rate",
  "audio_codec",
  "audio_sample_rate",
  "n_channels"
]
MEDIA_TYPES = []
EXTENSIONS = []
def read_ini ():
  global MEDIA_TYPES, EXTENSIONS
  scanner_ini = ini.Ini ("media_scanner.ini")
  MEDIA_TYPES = [i for i in scanner_ini.sections () if i not in ["general"]]
  EXTENSIONS = [i.lower () for i in scanner_ini.general.extensions.split (",")]

read_ini ()

def out_x_by_y (t):
  return "%dx%d" % t

def out_ratio (t):
  return "%d:%s" % t
  
def out_k (format):
  def _out_k (v):
    return format % (v / 1000.0)
  return _out_k

OUTPUTS = {
  "duration" : lambda x: "%2.2f s" % x,
  "screen_resolution" : out_x_by_y,
  "pixel_aspect_ratio" : out_ratio,
  "aspect_ratio" : out_ratio,
  "multiplex_bit_rate" : out_k ("%d kbps"),
  "video_bit_rate" : out_k ("%d kbps"),
  "audio_bit_rate" : out_k ("%d kbps"),
  "audio_sample_rate" : out_k ("%2.1f kHz")
}
class Media (object):
  
  def __init__ (self, filepath):
    self.filepath = filepath
    self.media = media.load (filepath)

    self.duration = self.media.duration
    self.screen_resolution = None
    self.aspect_ratio = None
    self.pixel_aspect_ratio = None
    self.video_format = None
    self.video_sample_bits = None
    self.audio_sample_bits = None
    self.frame_rate = None
    self.multiplex_bit_rate = None
    self.video_bit_rate = None
    self.audio_bit_rate = None
    self.audio_codec = None
    self.audio_sample_rate = None
    self.n_channels = None

    self.multiplex_bit_rate = 8 * filepath.size / self.media.duration
    
    if self.media.video_format:
      vf = self.media.video_format
      self.screen_resolution = (vf.width, vf.height)
      self.aspect_ratio = vf.display_aspect_ratio
      self.pixel_aspect_ratio = vf.pixel_aspect_ratio
      self.video_format = vf.codec_name
      self.frame_rate = vf.frame_rate
      self.video_sample_rate = vf.sample_rate
    
    if self.media.audio_format:
      af = self.media.audio_format
      if af.bytes_per_sample is None:
        self.audio_sample_bits is None
      else:
        self.audio_sample_bits = 8 * af.bytes_per_sample
      self.audio_bit_rate = af.bit_rate
      self.audio_codec = af.codec_name
      self.audio_sample_rate = af.sample_rate
      self.n_channels = af.channels
      
  def as_dict (self):
    d = {}
    for option in OPTIONS:
      value = getattr (self, option, None)
      if value is None:
        d[option] = None
      else:
        output_format = OUTPUTS.get (option, lambda x: x)
        d[option] = output_format (value)
    return d

def main (args):
  if len (args) >= 2:
    media_type = args[1].lower ()
  else:
    media_type = raw_input ("Media type (%s): " % (", ".join (MEDIA_TYPES)))
  spec = Spec (media_type)
    
  if len (args) >= 1:
    filepath = path (args[0])
  else:
    filepath = path (raw_input ("File / folder: "))

  if filepath.isfile ():
    media = [Media (filepath)]
  else:
    media = [Media (media_filepath) for media_filepath in filepath.walk () if media_filepath.endswith (EXTENSIONS)]

  for medium in media:
    print
    print medium.filepath
    results = spec.check (medium)
    for option in OPTIONS:
      print "  ", option, "=>", results.get (option, "N/A")

def x_by_y (text):
  return tuple (int (i) for i in text.split ("x"))
  
def ratio (text):
  return tuple (int (i) for i in text.split (":"))
  
def multiple (text):
  return [i.strip ().lower () for i in text.split (",")]

class Spec (object):
  
  FAIL, WARNING, PASS, NA = "FAIL", "WARNING", "PASS", "NA"
  MAP = {
    "duration" : (float, ["range"]),
    "screen_resolution" : (x_by_y, ["reversible"]),
    "aspect_ratio" : (ratio, ["reversible"]),
    "pixel_aspect_ratio" : (ratio, ["reversible"]),
    "video_format" : (str, ["multiple"]),
    "video_sample_bits" : (int, []),
    "audio_sample_bits" : (int, []),
    "frame_rate" : (float, ()),
    "multiplex_bit_rate" : (int, ["range"]),
    "video_bit_rate" : (int, ["range"]),
    "audio_bit_rate" : (int, ["range"]),
    "audio_codec" : (str, ["multiple"]),
    "audio_sample_rate" : (int, []),
    "n_channels" : (int, []),
  }
    
  def __init__ (self, media_type):
    self.options = {}
    scanner_ini = ini.Ini ("media_scanner.ini")
    media_types = [i for i in scanner_ini.sections () if i.lower () == media_type.lower ()]
    if not media_types:
      raise RuntimeError, "Media type %s has no specification" % media_type
    else:
      self.read (scanner_ini[media_types[0]])

  def read (self, section):
    for option, (converter, flags) in self.MAP.items ():
      value = section[option]
      if value is not None:
        if "multiple" in flags:
          self.options[option] = [converter (v.strip ()) for v in value.split (",")]
        elif "range" in flags:
          value = [converter (v.strip ()) for v in value.split ("-") if v.strip ()]
          if len (value) == 1: value = value + [value[0]]
          self.options[option] = value
        else:
          self.options[option] = converter (value)
        
  def check_item (self, spec_value, media_value, flags):
    if media_value is None or spec_value is None:
      return self.NA
    elif "range" in flags:
      lower, upper = spec_value
      if lower <= media_value <= upper:
        return self.PASS
      else:
        return self.FAIL
    elif "multiple" in flags:
      if media_value in spec_value:
        return self.PASS
      else:
        return self.FAIL
    elif spec_value == media_value:
      return self.PASS
    elif "reversible" in flags:
      if spec_value == media_value[::-1]:
        return self.WARNING
      else:
        return self.FAIL
    else:
      return self.FAIL
  
  def check (self, media):
    results = {}
    for option in OPTIONS:
      converter, flags = self.MAP[option]
      try:
        spec_value = self.options[option]
      except KeyError:
        results[option] = self.NA
      else:
        media_value = getattr (media, option)
        results[option] = self.check_item (spec_value, media_value, flags)
    
    return results
    
  def as_dict (self):
    return dict ((option, self.options.get (option)) for option in OPTIONS)

if __name__ == '__main__':
  main (sys.argv[1:])    
  raw_input ("Press enter...")
