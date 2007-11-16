cdef extern from "Python.h":

    ctypedef struct Py_ssize_t

    int PyCObject_Check(object o)
    object PyCObject_FromVoidPtr(void *, void (*destr)(void *))
    void *PyCObject_AsVoidPtr(object o)

    object PyString_FromStringAndSize(char *v, int len)
    int PyString_AsStringAndSize(object o, char **buf, int *length)

    void Py_INCREF(object o)
    void Py_DECREF(object o)

cdef extern from "string.h":
  void *memcpy (void *dest, void *src, int n)
  void *memset (void *s, int c, int n)

cdef public object c2py (void *ptr):
  return PyCObject_FromVoidPtr (ptr, NULL)

cdef void *py2c (object obj):
  return PyCObject_AsVoidPtr (obj)

cdef extern from "ffmpeg/avutil.h":

  struct AVRational:
    int num
    int den

cdef extern from "ffmpeg/avcodec.h":
  
  enum CodecType:
    CODEC_TYPE_UNKNOWN
    CODEC_TYPE_VIDEO
    CODEC_TYPE_AUDIO
    CODEC_TYPE_DATA
    CODEC_TYPE_SUBTITLE
    CODEC_TYPE_NB
    
  enum CodecID:
    pass

cdef extern from "ffmpeg/avformat.h":

  struct AVCodec:
    char *name
    CodecType type
    CodecID id
    int capabilities
    
  struct AVCodecContext:
    int bit_rate
    int flags
    int sub_id
    AVRational time_base
    int width
    int height
    int sample_rate
    int channels
    AVCodec *codec
    char codec_name[32]
    CodecType codec_type
    CodecID codec_id
    unsigned int codec_tag
    int bits_per_sample
    AVRational sample_aspect_ratio
    unsigned int stream_codec_tag
    float crf

  struct AVStream:
    int index
    int id
    AVCodecContext *codec
    AVRational r_frame_rate
    AVRational time_base
    int start_time
    int duration
    
  struct AVCodecTag:
    pass
  
  struct AVInputFormat:
    char *name
    char *long_name
    int flags
    AVCodecTag **codec_tag

  struct AVFormatContext:
    AVInputFormat *iformat
    unsigned int nb_streams
    AVStream *streams[20]
    char filename[1024]
    char title[512]
    int ctx_flags
    int start_time
    int duration
    int file_size
    int bit_rate
  
  struct AVFormatParameters:
    pass    

  void av_register_all ()
  int av_open_input_file (
    AVFormatContext **ic_ptr, 
    char *filename,
    AVInputFormat *fmt,
    int buf_size,
    AVFormatParameters *ap
  )
  int av_find_stream_info (AVFormatContext *ic)
  void av_close_input_file (AVFormatContext *ic)
  
cdef rational_to_tuple (AVRational rational):
  return (rational.num, rational.den)

class x_pydump (Exception):
  pass

cdef class Codec:
    
  cdef AVCodec *codec
  
  def __init__ (self, object codec):
    self.codec = <AVCodec *>py2c (codec)
    
  property name:
    def __get__ (self):
      return self.codec.name
  property type:
    def __get__ (self):
      return self.codec.type
  property id:
    def __get__ (self):
      return self.codec.id
  property capabilities:
    def __get__ (self):
      return self.codec.capabilities

cdef class CodecContext:

  cdef AVCodecContext *codec_context
  
  def __init__ (self, object codec_context):
    self.codec_context = <AVCodecContext *>py2c (codec_context)
    
  property bit_rate:
    def __get__ (self):
      return self.codec_context.bit_rate
  property flags:
    def __get__ (self):
      return self.codec_context.flags
  property sub_id:
    def __get__ (self):
      return self.codec_context.sub_id
  property time_base:
    def __get__ (self):
      return rational_to_tuple (self.codec_context.time_base)
  property size:
    def __get__ (self):
      return (self.codec_context.width, self.codec_context.height)
  property sample_rate:
    def __get__ (self):
      return self.codec_context.sample_rate
  property channels:
    def __get__ (self):
      return self.codec_context.channels
  property codec_name:
    def __get__ (self):
      return self.codec_context.codec_name
  property codec:
    def __get__ (self):
      if self.codec_context.codec is NULL:
        return None
      else:
        return Codec (c2py (self.codec_context.codec))
  property codec_type:
    def __get__ (self):
      return self.codec_context.codec_type
  property codec_id:
    def __get__ (self):
      return self.codec_context.codec_id
  property codec_tag:
    def __get__ (self):
      return self.codec_context.codec_tag
  property bits_per_sample:
    def __get__ (self):
      return self.codec_context.bits_per_sample
  property sample_aspect_ratio:
    def __get__ (self):
      return rational_to_tuple (self.codec_context.sample_aspect_ratio)
  property stream_codec_tag:
    def __get__ (self):
      return self.codec_context.stream_codec_tag
  property crf:
    def __get__ (self):
      return self.codec_context.crf

cdef class Stream:

  cdef AVStream *stream
  
  def __init__ (self, object stream):
    self.stream = <AVStream *>py2c (stream)
    
  property frame_rate:
    def __get__ (self):
      return rational_to_tuple (self.stream.r_frame_rate)
  property time_base:
    def __get__ (self):
      return rational_to_tuple (self.stream.time_base)
      
  property codec_context:
    def __get__ (self):
      return CodecContext (c2py (self.stream.codec))

cdef class FormatContext:

  cdef readonly char filename[256]
  cdef AVFormatContext *format_context
  
  def __init__ (self, char *filename):
    memcpy (self.filename, filename, 255)
    if av_open_input_file (&self.format_context, filename, NULL, 0, NULL) != 0:
      raise x_pydump, "Unable to open %s" % filename
    if av_find_stream_info (self.format_context) < 0:
      raise x_pydump, "No streams found in %s" % filename
      
  property n_streams:
    def __get__ (self):
      return self.format_context.nb_streams
      
  def stream (self, n_stream):
    if n_stream > self.format_context.nb_streams - 1:
      raise IndexError
    else:
      return Stream (c2py (self.format_context.streams[n_stream]))
      
  def __dealloc__ (self):
    av_close_input_file (self.format_context)

def open (char *filename):
  return FormatContext (filename)

def init ():
  av_register_all ()
