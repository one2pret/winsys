import pydump

def dump (obj):
  for i in (i for i in dir (obj) if not i.startswith ("_")):
    print i, "=>", getattr (obj, i)

video_file = pydump.open ("t3.m2v")
dump (video_file)
dump (video_file.stream (0))
dump (video_file.stream (0).codec_context)
codec = video_file.stream (0).codec_context.codec
print codec

## dump (video_file.stream (0).codec_context.codec)
