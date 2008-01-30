import os, sys
import glob
import re

def munge_html_files (dirname, filenames):
  for filename in filenames:
    filepath = os.path.join (dirname, filename)
    print filepath
    text = open (filepath).read ()
    text = re.sub ("(\n+)", "\n", text)
    text = re.sub ("(<META[^>]+>)", "\g<1>\n</head>\n<body>\n", text)
    open (filepath, "w").write (text)

def main (args=None):
  chm_filepath = os.path.join (sys.prefix, "lib", "site-packages", "PyWin32.chm")
  tempdir = "temp"
  if not os.path.exists (tempdir):
    os.mkdir (tempdir)
  os.system ("hh.exe -decompile %s %s" % (tempdir, chm_filepath))
  for dirname, dirnames, filenames in os.walk (tempdir):
    munge_html_files (dirname, filenames)
  
if __name__ == '__main__':
  main (sys.argv[1:])
