#include <ffmpeg/avcodec.h>
#include <ffmpeg/avformat.h>

#include <string.h>
#include <stdio.h>

void get_codec_name (
  char *buf,
  int buf_size,
  AVCodecContext *enc
)
{
  const char *codec_name;
  AVCodec *p;

  p = avcodec_find_decoder (enc->codec_id);

  if (p) {
    codec_name = p->name;
    if (enc->codec_id == CODEC_ID_MP3) {
      if (enc->sub_id == 2)
        codec_name = "mp2";
      else if (enc->sub_id == 1)
        codec_name = "mp1";
    }
  } else if (enc->codec_id == CODEC_ID_MPEG2TS) {
      /* fake mpeg2 transport stream codec (currently not
         registered) */
    codec_name = "mpeg2ts";
  } else if (enc->codec_name[0] != '\0') {
    codec_name = enc->codec_name;
  } else {
  char buf1[32];
    /* output avi tags */
    if (isprint(enc->codec_tag&0xFF) && isprint((enc->codec_tag>>8)&0xFF)
       && isprint((enc->codec_tag>>16)&0xFF) && isprint((enc->codec_tag>>24)&0xFF)){
        snprintf(buf1, sizeof(buf1), "%c%c%c%c / 0x%04X",
                 enc->codec_tag & 0xff,
                 (enc->codec_tag >> 8) & 0xff,
                 (enc->codec_tag >> 16) & 0xff,
                 (enc->codec_tag >> 24) & 0xff,
                  enc->codec_tag);
      } else {
          snprintf(buf1, sizeof(buf1), "0x%04x", enc->codec_tag);
      }
      codec_name = buf1;
  }

  strncpy (buf, codec_name, buf_size);
}

typedef struct _VideoInfo {
  char codec_name[256];
  int width;
  int height;
  int display_aspect_x;
  int display_aspect_y;
  int pixel_aspect_x;
  int pixel_aspect_y;
  int bitrate;
  float fps;
} VideoInfo;

typedef struct _AudioInfo {
  char codec_name[256];
  int n_channels;
  int sample_rate;
  int bitrate;
} AudioInfo;

void get_video_info (
  VideoInfo *video_info,
  AVStream *stream
)
{
AVCodecContext *enc = stream->codec;

  if (enc->width) {
    video_info->width = enc->width;
    video_info->height = enc->height;

    AVRational display_aspect_ratio;
    av_reduce(
      &display_aspect_ratio.num,
      &display_aspect_ratio.den,
      enc->width*enc->sample_aspect_ratio.num,
      enc->height*enc->sample_aspect_ratio.den,
      1024*1024
    );
    video_info->pixel_aspect_x = enc->sample_aspect_ratio.num;
    video_info->pixel_aspect_y = enc->sample_aspect_ratio.den;
    video_info->display_aspect_x = display_aspect_ratio.num;
    video_info->display_aspect_y = display_aspect_ratio.den;
  }
  else {
    video_info->width = 0;
    video_info->height = 0;
    video_info->pixel_aspect_x = 0;
    video_info->pixel_aspect_y = 0;
    video_info->display_aspect_x = 0;
    video_info->display_aspect_y = 0;
  }

  video_info->bitrate = enc->bit_rate;

  if (stream->r_frame_rate.den && stream->r_frame_rate.num)
    video_info->fps = av_q2d (stream->r_frame_rate);
  else
    video_info->fps = 1 / av_q2d (stream->codec->time_base);
}

void get_audio_info (
  AudioInfo *audio_info,
  AVStream *stream
)
{
AVCodecContext *enc = stream->codec;
  audio_info->n_channels = enc->channels;
  audio_info->sample_rate = enc->sample_rate;
  switch(enc->codec_id) {
    case CODEC_ID_PCM_S32LE:
    case CODEC_ID_PCM_S32BE:
    case CODEC_ID_PCM_U32LE:
    case CODEC_ID_PCM_U32BE:
      audio_info->bitrate = enc->sample_rate * enc->channels * 32;
      break;
    case CODEC_ID_PCM_S24LE:
    case CODEC_ID_PCM_S24BE:
    case CODEC_ID_PCM_U24LE:
    case CODEC_ID_PCM_U24BE:
    case CODEC_ID_PCM_S24DAUD:
      audio_info->bitrate = enc->sample_rate * enc->channels * 24;
      break;
    case CODEC_ID_PCM_S16LE:
    case CODEC_ID_PCM_S16BE:
    case CODEC_ID_PCM_U16LE:
    case CODEC_ID_PCM_U16BE:
      audio_info->bitrate = enc->sample_rate * enc->channels * 16;
      break;
    case CODEC_ID_PCM_S8:
    case CODEC_ID_PCM_U8:
    case CODEC_ID_PCM_ALAW:
    case CODEC_ID_PCM_MULAW:
      audio_info->bitrate = enc->sample_rate * enc->channels * 8;
      break;
    default:
      audio_info->bitrate = enc->bit_rate;
      break;
  }

}

int main (int argc, char *argv[]) {
  AVFormatContext *pFormatCtx;
  int             i, videoStream, audioStream;
  AVCodecContext  *pCodecCtx;
  AVCodec         *pCodec;

  if(argc < 2) {
    printf("Please provide a movie file\n");
    return -1;
  }
  // Register all formats and codecs
  av_register_all();

  // Open video file
  if(av_open_input_file(&pFormatCtx, argv[1], NULL, 0, NULL)!=0)
    return -1; // Couldn't open file

  // Retrieve stream information
  if(av_find_stream_info(pFormatCtx)<0)
    return -1; // Couldn't find stream information

  for(i=0; i<pFormatCtx->nb_streams; i++) {
    AVCodecContext *codec = pFormatCtx->streams[i]->codec;
    int codec_type = codec->codec_type;

    fprintf (stderr, "\n\n");

    if (codec_type == CODEC_TYPE_VIDEO) {
      VideoInfo video_info;
      fprintf (stderr, "VIDEO\n");
      get_codec_name (video_info.codec_name, sizeof (video_info.codec_name), codec);
      get_video_info (&video_info, pFormatCtx->streams[i]);

      fprintf (stderr, "CODEC: %s\n", video_info.codec_name);
      fprintf (stderr, "WxH: %dx%d\n", video_info.width, video_info.height);
      fprintf (stderr, "PAR: [%d:%d]\n", video_info.pixel_aspect_x, video_info.pixel_aspect_y);
      fprintf (stderr, "DAR: [%d:%d]\n", video_info.display_aspect_x, video_info.display_aspect_y);
      fprintf (stderr, "Bit rate: %d\n", video_info.bitrate);
      fprintf (stderr, "fps: %3.2f\n", video_info.fps);
    }
    if (codec_type == CODEC_TYPE_AUDIO) {
      AudioInfo audio_info;
      fprintf (stderr, "AUDIO\n");
      get_codec_name (audio_info.codec_name, sizeof (audio_info.codec_name), codec);
      get_audio_info (&audio_info, pFormatCtx->streams[i]);

      fprintf (stderr, "CODEC: %s\n", audio_info.codec_name);
      fprintf (stderr, "n_channels: %d\n", audio_info.n_channels);
      fprintf (stderr, "sample rate: %d\n", audio_info.sample_rate);
      fprintf (stderr, "bitrate: %d\n", audio_info.bitrate);
    }
  }

  // Close the video file
  av_close_input_file(pFormatCtx);

  return 0;
}
