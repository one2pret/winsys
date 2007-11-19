import os, sys
import re
import subprocess

def reduced (fraction):
    def _gcd (fraction):
        a, b = fraction
        while b:
            a, b = b, a % b
        return a
    
    gcd = _gcd (fraction)
    return fraction[0] / gcd, fraction[1] / gcd

matcher = re.compile (r"([A-Z_]+)\W*:\W*(\w+)")

OPTIONS = {
  "VIDEO_DURATION" : int,
  "VIDEO_CODEC" : unicode,
  "VIDEO_SUBID" : int,
  "VIDEO_WIDTH" : int,
  "VIDEO_HEIGHT" : int,
  "VIDEO_PARX" : int,
  "VIDEO_PARY" : int,
  "VIDEO_BIT_RATE" : int,
  "VIDEO_FRAME_RATE_NUM" : int,
  "VIDEO_FRAME_RATE_DEN" : int,
  "VIDEO_TIME_BASE_NUM" : int,
  "VIDEO_TIME_BASE_DEN" : int,
  "VIDEO_BIT_RATE" : int,
  "VIDEO_SAMPLE_RATE" : int,
  "AUDIO_CODEC" : unicode,
  "AUDIO_SUBID" : int,
  "AUDIO_N_CHANNELS" : int,
  "AUDIO_SAMPLE_RATE" : int,
  "AUDIO_BIT_RATE" : int,
  "AUDIO_SAMPLE_BITS" : int
}

def file_details (filepath):
  stdout = subprocess.Popen (["dump.exe", filepath], stdout=subprocess.PIPE).stdout
  details = {}
  for k, v in matcher.findall (stdout.read ()):
    converter = OPTIONS.get (k, unicode)
    details[k] = converter (v)
  return details

class Stream (object):
  pass

class Media (object):
  
  def __init__ (self, filename=None):
    self.duration = None
    self.video_format = Stream ()
    self.audio_format = Stream ()
    if filename:
      self.load (filename)
    
  def load (self, filename):
    details = file_details (filename)
    vf = self.video_format
    vf.width = details.get ("VIDEO_WIDTH")
    vf.height = details.get ("VIDEO_HEIGHT")
    vf.pixel_aspect_ratio = (details.get ("VIDEO_PARX", 1), details.get ("VIDEO_PARY", 1))
    darx = vf.width * vf.pixel_aspect_ratio[0]
    dary = vf.height * vf.pixel_aspect_ratio[1]
    vf.display_aspect_ratio = reduced ((darx, dary))
    vf.codec_name = details.get ("VIDEO_CODEC")
    vf.subid = details.get ("VIDEO_SUBID")
    frame_rate_num = details.get ("VIDEO_FRAME_RATE_NUM")
    frame_rate_den = details.get ("VIDEO_FRAME_RATE_DEN")
    time_base_num = details.get ("VIDEO_TIME_BASE_NUM")
    time_base_den = details.get ("VIDEO_TIME_BASE_DEN")
    if time_base_num and time_base_den:
      vf.time_base = 1.0 * time_base_num / time_base_den
    else:
      vf.time_base = 1.0
    if frame_rate_num and frame_rate_den:
      vf.frame_rate = 1.0 * frame_rate_num / frame_rate_den
    else:
      vf.frame_rate = 1.0 / vf.time_base
    vf.sample_rate = details.get ("VIDEO_SAMPLE_RATE")
    vf.bit_rate = details.get ("VIDEO_BIT_RATE")
    
    af = self.audio_format
    audio_sample_bits = details.get ("AUDIO_SAMPLE_BITS")
    if audio_sample_bits is None:
      af.bytes_per_sample = None
    else:
      af.bytes_per_sample = audio_sample_bits / 8
    af.bit_rate = details.get ("AUDIO_BIT_RATE")
    af.codec_name = details.get ("AUDIO_CODEC")
    af.subid = details.get ("AUDIO_SUBID")
    af.sample_rate = details.get ("AUDIO_SAMPLE_RATE")
    af.channels = details.get ("AUDIO_N_CHANNELS")

    self.duration = details.get ("VIDEO_DURATION", 0.0) * vf.time_base
  
  def __str__ (self):
    def dump (obj):
      return "{\n  %s\n}" % "\n  ".join ("%s => %s" % (k, v) for (k, v) in obj.__dict__.items () if not k.startswith ("_"))
    return "VIDEO\n" + dump (self.video_format) + "\nAUDIO\n" + dump (self.audio_format)

def load (filename):
  return Media (filename)
  

if __name__ == '__main__':
  print file_details ("t3.m2v")
