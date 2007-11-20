import os, sys
from path import path
import ffmpeg

def dump (obj):
  for i in (i for i in dir (obj) if not i.startswith ("_")):
    print i, "=>", getattr (obj, i)

def dump_mediafile (mediapath):
  print
  print mediapath
  video_file = ffmpeg.open (mediapath)
  dump (video_file)
  if video_file.n_streams == 0:
    print "No streams"
  else:
    dump (video_file.stream (0))
    dump (video_file.stream (0).codec_context)
    codec = video_file.stream (0).codec_context.codec
    if codec:
      dump (codec)
    else:
      print "No Codec"
  
if __name__ == '__main__':
  if len (sys.argv) > 1:
    filepath = path (sys.argv[1])
  else:
    filepath = path ("media")
  
  if filepath.isdir ():
    for mediapath in filepath.files ():
      dump_mediafile (mediapath)
  else:
    dump_mediafile (filepath)
