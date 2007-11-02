import os, sys
import csv
import traceback

from path import path
import win32com.client

import media_player

MEDIA_EXTENSIONS = ['mpg', 'mp4', 'divx', 'wmv', 'mov', 'avi']
CSV_FILENAME = "scan-media.csv"
CSV_FIELDS = ["filename", "title", "duration", "size", "aspect_ratio", "audio_format", "audio_bitrate", "video_format", "video_bitrate", "video_frame_rate"]

def show_media_details (media_filepath, fields):
  sys.stderr.write (media_filepath + "\n")
  try:
    wmedia = media_player.player.mediaCollection.add (media_filepath)
    media = media_player.Media (media_filepath, wmedia)
  except:
    sys.stderr.write ("*** UNABLE TO LOAD FILE ***\n")
    return {}

  try:
    return dict ((field, getattr (media, field)) for field in fields)
  finally:
    media_player.player.mediaCollection.remove (wmedia, False)

def main (args=[]):
  if args:
    media_path = path (args[0])
  else:
    media_path = path (raw_input ("Folder/File: "))

  f = open (CSV_FILENAME, "wb")
  try:
    csv_writer = csv.writer (f)
    csv_writer.writerow (CSV_FIELDS)
    if media_path.isfile ():
      details = show_media_details (os.path.abspath (media_path), CSV_FIELDS)
      if details:
        csv_writer.writerow ([details[field] for field in CSV_FIELDS])
    else:
      media_files = []
      for dirpath, dirnames, filenames in os.walk (media_path):
        for filename in filenames:
          for extension in MEDIA_EXTENSIONS:
            if filename.lower ().endswith (extension):
              details = show_media_details (os.path.abspath (os.path.join (dirpath, filename)), CSV_FIELDS)
              if details:
                csv_writer.writerow ([details[field] for field in CSV_FIELDS])
  finally:
    f.close ()

if __name__ == '__main__':
  main (sys.argv[1:])
  os.startfile (CSV_FILENAME)