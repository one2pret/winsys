cdef extern from "ffmpeg/avformat.h":

  struct AVInputFormat:
    pass
  
  struct AVFormatContext:
    pass
    
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

av_register_all ()
cdef AVFormatContext *format_context
cdef int result 
result = av_open_input_file (&format_context, "s.avi", NULL, 0, NULL)
print result
