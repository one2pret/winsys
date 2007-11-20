#include <ffmpeg/avcodec.h>
#include <ffmpeg/avformat.h>

#include "stdio.h"

int main (int argc, char *argv[]) {
  AVFormatContext *pFormatCtx;
  av_register_all ();
  int result = av_open_input_file (&pFormatCtx, "s.avi", NULL, 0, NULL);
  printf ("Result: %d\n", result);
  return 0;
}
