import os, sys
import glob
import re
import htmlentitydefs

import html2rst

def munged_text (text):
  text = re.sub (r"(\n+)", r"\n", text)
  text = re.sub (r"(<META[^>]+>)", r"\g<1>\n</head>\n<body>\n", text)
  for entitydef in htmlentitydefs.entitydefs.keys ():
    text = re.sub (r"(&%s[^;])" % entitydef, "&%s;" % entitydef, text)
  text = re.sub (r"(&#\d+)[^;]", "\g<1>;", text)
  
  #
  # Fixup unclosed <LI>
  #
  lines = []
  for line in text.lower ().splitlines ():
    if line.startswith ("<li>") and not line.endswith ("</li>"):
      lines.append (line + "</li>")
    else:
      lines.append (line)
  text = "\n".join (lines)
  
  return html2rst.html2text (text)

def main (args=None):
  chm_filepath = os.path.join (sys.prefix, "lib", "site-packages", "PyWin32.chm")
  html_tempdir = "htmltemp"
  rst_tempdir = "rsttemp"
  if not os.path.exists (html_tempdir): os.mkdir (html_tempdir)
  if not os.path.exists (rst_tempdir): os.mkdir (rst_tempdir)
  
  os.system ("hh.exe -decompile %s %s" % (html_tempdir, chm_filepath))
  for dirname, dirnames, filenames in os.walk (html_tempdir):
    for filename in filenames:
      if not filename.endswith (".html"): continue
      print filename
      base, ext = os.path.splitext (filename)
      try:
        open (os.path.join (rst_tempdir, "%s.rst" % base), "w").write (
          munged_text (open (os.path.join (dirname, filename)).read ()).encode ("utf8")
        )
      except:
        print repr (munged_text (open (os.path.join (dirname, filename)).read ()))
        raise
  
if __name__ == '__main__':
  main (sys.argv[1:])
