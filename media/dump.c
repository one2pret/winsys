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

typedef struct _Info {
  char codec_type[10];
  char codec_name[256];
  int duration;
  int sub_id;
  int width;
  int height;
  int pixel_aspect_x;
  int pixel_aspect_y;
  int bit_rate;
  int frame_rate_num;
  int frame_rate_den;
  int time_base_num;
  int time_base_den;
  int sample_rate;  
  int sample_bits;
  int n_channels;
} Info;

void get_info (
  const char *codec_type,
  Info *info,
  AVStream *stream
)
{
AVCodecContext *enc = stream->codec;

  strncpy (info->codec_type, codec_type, 10);
  info->sub_id = enc->sub_id;
  info->width = enc->width;
  info->height = enc->height;
  info->pixel_aspect_x = enc->sample_aspect_ratio.num;
  info->pixel_aspect_y = enc->sample_aspect_ratio.den;
  info->bit_rate = enc->bit_rate;
  info->frame_rate_num = stream->r_frame_rate.num;
  info->frame_rate_den = stream->r_frame_rate.den;
  info->time_base_num = stream->time_base.num;
  info->time_base_den = stream->time_base.den;
  info->sample_rate = enc->sample_rate;
  info->duration = stream->duration;
  info->n_channels = enc->channels;
  info->sample_rate = enc->sample_rate;
  switch (enc->sample_fmt)
  {
      case SAMPLE_FMT_U8:
          info->sample_bits = 8;
          break;
      case SAMPLE_FMT_S16:
          info->sample_bits = 16;
          break;
      case SAMPLE_FMT_S24:
          info->sample_bits = 24;
          break;
      case SAMPLE_FMT_S32:
          info->sample_bits = 32;
          break;
      case SAMPLE_FMT_FLT:
          info->sample_bits = 32;
          break;
  }
  switch (enc->codec_id)
  {
      case CODEC_ID_PCM_S32LE:
      case CODEC_ID_PCM_S32BE:
      case CODEC_ID_PCM_U32LE:
      case CODEC_ID_PCM_U32BE:
      case CODEC_ID_PCM_S24LE:
      case CODEC_ID_PCM_S24BE:
      case CODEC_ID_PCM_U24LE:
      case CODEC_ID_PCM_U24BE:
      case CODEC_ID_PCM_S24DAUD:
      case CODEC_ID_PCM_S16LE:
      case CODEC_ID_PCM_S16BE:
      case CODEC_ID_PCM_U16LE:
      case CODEC_ID_PCM_U16BE:
      case CODEC_ID_PCM_S8:
      case CODEC_ID_PCM_U8:
      case CODEC_ID_PCM_ALAW:
      case CODEC_ID_PCM_MULAW:
          info->bit_rate = enc->sample_rate * 
              enc->channels * info->sample_bits;
          break;
      default:
          info->bit_rate = enc->bit_rate;
          break;
  }
}

int main (int argc, char *argv[]) {
  AVFormatContext *pFormatCtx;
  int             i, videoStream, audioStream;

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

    if (codec_type == CODEC_TYPE_VIDEO) {
      Info video_info;
      get_codec_name (video_info.codec_name, sizeof (video_info.codec_name), codec);
      get_info ("VIDEO", &video_info, pFormatCtx->streams[i]);
      
      fprintf (stdout, "VIDEO_CODEC: %s\n", video_info.codec_name);
      fprintf (stdout, "VIDEO_DURATION: %d\n", video_info.duration);
      fprintf (stdout, "VIDEO_SUBID: %d\n", video_info.sub_id);
      fprintf (stdout, "VIDEO_WIDTH: %d\n", video_info.width);
      fprintf (stdout, "VIDEO_HEIGHT: %d\n", video_info.height);
      fprintf (stdout, "VIDEO_PARX: %d\n", video_info.pixel_aspect_x);
      fprintf (stdout, "VIDEO_PARY: %d\n", video_info.pixel_aspect_y);
      fprintf (stdout, "VIDEO_BIT_RATE: %d\n", video_info.bit_rate);
      fprintf (stdout, "VIDEO_FRAME_RATE_NUM: %d\n", video_info.frame_rate_num);
      fprintf (stdout, "VIDEO_FRAME_RATE_DEN: %d\n", video_info.frame_rate_den);
      fprintf (stdout, "VIDEO_TIME_BASE_NUM: %d\n", video_info.time_base_num);
      fprintf (stdout, "VIDEO_TIME_BASE_DEN: %d\n", video_info.time_base_den);
      fprintf (stdout, "VIDEO_SAMPLE_RATE: %d\n", video_info.sample_rate);
      fprintf (stdout, "VIDEO_SAMPLE_BITS: %d\n", video_info.sample_bits);
      fprintf (stdout, "VIDEO_CHANNELS: %d\n", video_info.n_channels);
    }
    if (codec_type == CODEC_TYPE_AUDIO) {
      Info audio_info;
      get_codec_name (audio_info.codec_name, sizeof (audio_info.codec_name), codec);
      get_info ("AUDIO", &audio_info, pFormatCtx->streams[i]);
    
      fprintf (stdout, "AUDIO_CODEC: %s\n", audio_info.codec_name);
      fprintf (stdout, "AUDIO_DURATION: %d\n", audio_info.duration);
      fprintf (stdout, "AUDIO_SUBID: %d\n", audio_info.sub_id);
      fprintf (stdout, "AUDIO_WIDTH: %d\n", audio_info.width);
      fprintf (stdout, "AUDIO_HEIGHT: %d\n", audio_info.height);
      fprintf (stdout, "AUDIO_PARX: %d\n", audio_info.pixel_aspect_x);
      fprintf (stdout, "AUDIO_PARY: %d\n", audio_info.pixel_aspect_y);
      fprintf (stdout, "AUDIO_BIT_RATE: %d\n", audio_info.bit_rate);
      fprintf (stdout, "AUDIO_FRAME_RATE_NUM: %d\n", audio_info.frame_rate_num);
      fprintf (stdout, "AUDIO_FRAME_RATE_DEN: %d\n", audio_info.frame_rate_den);
      fprintf (stdout, "AUDIO_TIME_BASE_NUM: %d\n", audio_info.time_base_num);
      fprintf (stdout, "AUDIO_TIME_BASE_DEN: %d\n", audio_info.time_base_den);
      fprintf (stdout, "AUDIO_SAMPLE_RATE: %d\n", audio_info.sample_rate);
      fprintf (stdout, "AUDIO_SAMPLE_BITS: %d\n", audio_info.sample_bits);
      fprintf (stdout, "AUDIO_CHANNELS: %d\n", audio_info.n_channels);
    }
  }

  // Close the video file
  av_close_input_file(pFormatCtx);

  return 0;
}
