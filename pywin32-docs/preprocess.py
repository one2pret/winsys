import os, sys
import glob
import htmlentitydefs
import re
import traceback

import html2rst
from BeautifulSoup import MinimalSoup

UNWANTED_MARKUP = ["html", "body", "head"]
UNWANTED_RE = re.compile ("|".join ("<%s>|</%s>" % (markup, markup) for markup in UNWANTED_MARKUP), re.IGNORECASE)
UNWANTED_TITLE_RE = re.compile (r"<title>.*</title>", re.IGNORECASE)
UNWANTED_LEADING_HR = re.compile (r"^-*\n*")

def munged_text (text):
  #
  # Fix up entity & character defs so they end with semicolons
  #
  for entitydef in htmlentitydefs.entitydefs.keys ():
    text = re.sub (r"(&%s)(?!;)" % entitydef, "\g<1>;", text)
  text = re.sub (r"(&#\d+)(?!;)", "\g<1>;", text)
  text = re.sub (r"<title>[^<]*</title>", "", text, re.IGNORECASE)
  text = UNWANTED_RE.sub ("", text)
  text = UNWANTED_TITLE_RE.sub ("", text)
  text = "\n".join (line + "</li>" if line.lower ().startswith ("<li>") and "</li>" not in line.lower () else line for line in text.splitlines ())
  soup = unicode (text, "cp1252")
  
  try:
    rst = html2rst.html2text (soup)
  except:
    print soup
    raise
  else:
    rst = UNWANTED_LEADING_HR.sub ("", rst)
    if not rst.strip ():
      raise RuntimeError, "No RST"
    else:
      return rst

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
      html_filepath = os.path.join (html_dirname, filename)
      print "  ", html_filepath
      base, ext = os.path.splitext (filename)
      rst_filepath = os.path.join (rst_dirname, "%s.rst" % base)
      if os.path.exists (rst_filepath) and os.path.getmtime (rst_filepath) > os.path.getmtime (html_filepath):
        continue
      else:
        open (rst_filepath, "w").write (
          munged_text (open (html_filepath).read ()).encode ("utf8")
        )
  
if __name__ == '__main__':
  main (sys.argv[1:])
