"""doc2file - convert a Word document to a pcl file

Usage: python doc2file.py --in=[input file] --out=[output file] --printer=[name of printer]
(Defaults are: none, <input> + .prn and "cas" respectively)

eg
  python doc2file.py --in=c:/temp/spec.doc --out=c:/temp/spec.prn --printer=cas
"""
import os, sys
import glob
import shutil
import tempfile
import time

import win32com.client
import pythoncom

def doc2file (word_filepath, printer_name, filepath, debug=0):
  """doc2file - Convert one word document to a printer file.
  """
  word_filepath = os.path.abspath (word_filepath)
  filepath = os.path.abspath (filepath)
  print os.path.basename (word_filepath), "=>", os.path.basename (filepath)

  pythoncom.CoInitializeEx (pythoncom.COINIT_APARTMENTTHREADED)
  word = win32com.client.DispatchEx ("Word.Application")
  try:
    active_printer = word.ActivePrinter
    if debug:
      print "About to set active printer to", printer_name
    word.ActivePrinter = printer_name
  
    doc = word.Documents.Open (word_filepath, False, False, False)
    doc.Saved = True
    word.NormalTemplate.Saved = True
  
    #
    # Print in the background, and keep polling
    #  until printing is complete.
    #
    word.PrintOut (True, False, 0, filepath)
    while word.BackgroundPrintingStatus > 0:
      time.sleep (0.1)
  
    doc.Close ()
    word.ActivePrinter = active_printer
  finally:
    word.Quit ()
    try:
      del doc
    except NameError:
      pass
    try:
      del word
    except NameError:
      pass
    pythoncom.CoUninitialize ()

def doc2file_directory (input_dir, output_dir, printer, extension, debug=0):
  """doc2file_directory - convert all the DOCs in a directory to print files
  """
  input_dir = os.path.normpath (input_dir)
  output_dir = os.path.normpath (output_dir)
  if debug: print "Converting from %s to %s" % (input_dir, output_dir)
  
  #
  # Remove all existing files of the output type in
  #  the output directory
  #
  for f in glob.glob (os.path.join (output_dir, "*.%s" % extension)):
    os.remove (f)

  #
  # FOR each file in the temporary input directory LOOP
  #   Run GhostScript against the file to the temporary output directory
  # END LOOP
  #
  pattern = os.path.join (input_dir, "*.doc")
  for filename in glob.glob (pattern):
    input_filename = os.path.normpath (filename)
    (inputpath, inputfile) = os.path.split (input_filename)
    outputfile = (os.path.splitext (inputfile)[0] + "." + extension).upper ()
    output_filename = os.path.join (output_dir, outputfile)
    
    doc2file (input_filename, printer, output_filename, extension, debug)

if __name__ == '__main__':
  from optparse import OptionParser

  parser = OptionParser ()
  parser.add_option (
    "-i", "--in",
    action="store", type="string", dest="input_filename",
    help="Word doc filename", default="."
  )
  parser.add_option (
    "-o", "--out",
    action="store", type="string", dest="output_filename",
    help="PCL filename"
  )
  parser.add_option (
    "--printer",
    action="store", type="string", dest="printer",
    default = "Cas",
    help="Printer to use"
  )
  parser.add_option (
    "--debug",
    action="store", type="int", dest="debug",
    help="Debug level", default="0"
  )
  (options, args) = parser.parse_args ()

  input_filename = options.input_filename
  output_filename = options.output_filename
  if output_filename is None:
    path, filename = os.path.split (input_filename)
    base, ext = os.path.splitext (filename)
    output_filename = os.path.join (path, "%s.prn" % base)
  printer = options.printer

  doc2file (input_filename, printer, output_filename, options.debug)
