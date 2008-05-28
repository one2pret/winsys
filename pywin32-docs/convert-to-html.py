from __future__ import with_statement
import os, sys
import htmlentitydefs
import re
import sgmllib
import tempfile

class FixupParser (sgmllib.SGMLParser):
  """Fix-up parser to scan the contents file generated
  by HTMLHelp, generate a suitable HTML output file for
  use within standard HTML files and to provide a
  root-to-leaf mapping for use as a breadcrumb trail
  in individual pages.
  """
  
  def __init__ (self, infile, outfile):
    sgmllib.SGMLParser.__init__ (self)
    self.infile = infile
    self.outfile = outfile
    
    self.inside_li = False
    self.inside_object = False
    self.link_name = self.link_url = ""
    self.trail = []
    self.contents_map = {}
  
  def start (self):
    self.feed (self.infile.read ())
    
  def output (self, text):
    self.outfile.write (text + "\n")
    
  def start_ul (self, attrs):
    """If we're starting a list, close any unclosed
    list item and add the latest (ie this) url/name
    pair to the trail."""
    if self.inside_li:
      self.end_li ()
    self.output ("<ul>")
    if self.link_url:
      self.trail.append ((self.link_url, self.link_name))
    
  def end_ul (self):
    """If we're finishing a list, close any unclosed
    list item and pop this url/name off the trail."""
    if self.inside_li:
      self.end_li ()
    self.output ("</ul>")
    if self.trail:
      self.trail.pop ()

  def start_li (self, attrs):
    """If we're starting a list item, make a note of the
    fact so we can track objects within it."""
    if self.inside_li:
      self.end_li ()
    self.output ("<li>")
    self.inside_li = True
  
  def end_li (self):
    """If we're finishing a list item, make a note so no
    objects are tracked which are outside a list item."""
    self.output ("</li>")
    self.inside_li = False
  
  def start_object (self, attrs):
    """The text/sitemap objects hold the real indexing info.
    Note that we're inside such an object so that we pick up
    its parameters."""
    attrs = dict (attrs)
    if attrs.get ("type") == "text/sitemap":
      if self.inside_object:
        self.end_object ()
      self.link_name = self.link_url = ""
      self.inside_object = True
    
  def end_object (self):
    """At the end of an object tag, add the trail so far to
    the entry for this item's index and output an appropriate
    href."""
    if self.inside_object:
      self.contents_map[self.link_url] = self.trail[:]
      if self.trail and self.trail[-1][0] <> self.link_url:
        self.contents_map[self.link_url].append (("", self.link_name))
      self.output ('<a href="%s">%s</a>' % (self.link_url, self.link_name))
      self.inside_object = False

  """An object's param items are where the indexing info is
  stored. A "Name" param holds the name of the page; a "Local"
  item holds the slightly mungified URL which we strip before
  storing."""
  def start_param (self, attrs):
    UNWANTED_PREAMBLE = "mk:@MSITStore:PyWin32.chm::/"
    if self.inside_object:
      attrs = dict (attrs)
      if attrs.get ("name") == "Name":
        self.link_name = attrs.get ("value", "<Unnamed>")
      elif attrs.get ("name") == "Local":
        link_url = attrs.get ("value")
        if link_url:
          self.link_url = link_url[len (UNWANTED_PREAMBLE):]
        else:
          self.link_url = "<Unlinked>"

UNWANTED_MARKUP = ["html", "body", "head"]
UNWANTED_RE = re.compile ("|".join ("<%s>|</%s>" % (markup, markup) for markup in UNWANTED_MARKUP), re.IGNORECASE)
UNWANTED_TITLE_RE = re.compile (r"<title>.*</title>", re.IGNORECASE)
UNWANTED_GENERATOR = r'<META NAME="GENERATOR" CONTENT="Autoduck, by erica@microsoft.com">'

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
  text = text.replace (UNWANTED_GENERATOR, "")
  text = u"\n".join (line + u"</li>" if line.lower ().startswith (u"<li>") and u"</li>" not in line.lower () else line for line in text.splitlines ())
  return text
  
INDEX_CONTENT = """
<h1>PyWin32 Documentation</h1>

<p>This documentation is generated from the .chm file which is shipped with
the PyWin32 extensions for Python. Apart from absolutely essential cleanups
to make the HTML display properly, no changes have been made.</p>

<ul>
<li> <a href="contents.html">Table of Contents</a> </li>
<li> <a href="PyWin32.html">Front Page</a> </li>
</ul>
"""

#
# Navigation is a separate string so that it can be
# excluded from, eg, the contents page.
#
NAVIGATION_HTML = """
<div class="navigation">
  <a href="%(root_path)s%(toc_filename)s">Contents</a> | %(breadcrumbs)s
</div>
"""

HTML = """
<html>
  <head>
    <title>%(title)s</title>
    <link href="%(root_path)s%(css_filename)s" rel="stylesheet" type="text/css" media="all">
  </head>
  <body>
    %(navigation)s
    <div id="content">
      %(content)s
    </div>
  </body>
</html>
"""

def main (args=None):
  chm_filepath = os.path.join (sys.prefix, "lib", "site-packages", "PyWin32.chm")
  html_tempdir = "htmltemp"
  html2_tempdir = "../pywin32-docs"
  css_filename = "pywin32.css"
  toc_filename = "contents.html"
  
  print "Decompiling .chm..."
  if not os.path.exists (html_tempdir): 
    os.mkdir (html_tempdir)
  os.system ("hh.exe -decompile %s %s" % (html_tempdir, chm_filepath))
  
  print "Copying stylesheet..."
  if not os.path.exists (html2_tempdir): 
    os.mkdir (html2_tempdir)
  open (os.path.join (html2_tempdir, css_filename), "w").write (open (css_filename).read ())
  
  print "Writing index.html..."
  with open (os.path.join (html2_tempdir, "index.html"), "w") as outfile:
    title = "PyWin32 Documentation"
    navigation = ""
    root_path = ""
    content = INDEX_CONTENT
    outfile.write (HTML % locals ())
  
  print "Generating contents..."
  with open (os.path.join (html_tempdir, "pywin32.hhc")) as infile:
    handle, filename = tempfile.mkstemp ()
    with open (filename, "w") as outfile:
      parser = FixupParser (infile, outfile)
      parser.start ()
  contents_map = parser.contents_map
      
  print "Writing table of contents..."
  with open (os.path.join (html2_tempdir, toc_filename), "w") as outfile:
    title = "PyWin32 Documentation"
    content = open (filename).read ()
    root_path = ""
    css_filename = css_filename
    navigation = ""
    outfile.write (HTML % locals ())
  
  for html_dirname, dirnames, filenames in os.walk (html_tempdir):
    html2_dirname = os.path.join (html2_tempdir, html_dirname[1+len (html_tempdir):])
    print html_dirname, "=>", html2_dirname
    if not os.path.exists (html2_dirname):
      os.mkdir (html2_dirname)
    
    for filename in filenames:
      if not filename.lower ().endswith (".html"): continue
      html_filepath = os.path.join (html_dirname, filename)
      print "  %s (%d)" % (html_filepath, html_filepath.count ("\\")-1)
      base, ext = os.path.splitext (filename)
      html2_filepath = os.path.join (html2_dirname, "%s.html" % base)
      depth = html_filepath.count ("\\") - 1
      root_path = "../" * depth
      
      content = unicode (open (html_filepath).read (), "cp1252")
      content = munged_text (content)
      for title in re.findall (r"<h1>([^<]+)</h1>", content, re.IGNORECASE):
        break
      else:
        title = filename
      relative_filepath = html_filepath[1+len (html_tempdir):].replace ("\\", "/")
      breadcrumb_trail = contents_map.get (relative_filepath, [])
      breadcrumbs = " &gt; ".join (('<a href="%s">%s</a>' % (url, name) if url else name) for (url, name) in breadcrumb_trail)
      navigation = NAVIGATION_HTML % locals ()
      html = HTML % locals ()
      open (html2_filepath, "w").write (html.encode ("utf8"))

if __name__ == '__main__':
  main (sys.argv[1:])
