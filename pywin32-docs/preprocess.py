import os, sys
import glob
import re
import htmlentitydefs

import html2rst
from BeautifulSoup import MinimalSoup

def munged_text (text):
  #
  # Fix up entity & character defs so they end with semicolons
  #
  for entitydef in htmlentitydefs.entitydefs.keys ():
    text = re.sub (r"(&%s)(?!;)" % entitydef, "\g<1>;", text)
  text = re.sub (r"(&#\d+)(?!;)", "\g<1>;", text)  
  return html2rst.html2text (unicode (MinimalSoup (text)))

def main (args=None):
  chm_filepath = os.path.join (sys.prefix, "lib", "site-packages", "PyWin32.chm")
  html_tempdir = "htmltemp"
  rst_tempdir = "rsttemp"
  
  if not os.path.exists (html_tempdir): 
    os.mkdir (html_tempdir)
    os.system ("hh.exe -decompile %s %s" % (html_tempdir, chm_filepath))
  
  if not os.path.exists (rst_tempdir): 
    os.mkdir (rst_tempdir)
  for html_dirname, dirnames, filenames in os.walk (html_tempdir):
    rst_dirname = os.path.join (rst_tempdir, html_dirname[1+len (html_tempdir):])
    print html_dirname, "=>", rst_dirname
    if not os.path.exists (rst_dirname):
      os.mkdir (rst_dirname)
    for filename in filenames:
      if not filename.endswith (".html"): continue
      filepath = os.path.join (html_dirname, filename)
      print "  ", filepath
      base, ext = os.path.splitext (filename)
      open (os.path.join (rst_dirname, "%s.rst" % base), "w").write (
        munged_text (open (filepath).read ()).encode ("utf8")
      )
  
if __name__ == '__main__':
  main (sys.argv[1:])
