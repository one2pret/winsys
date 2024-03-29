import os, sys
import glob
import imp
import unittest as unittest0
try:
  unittest0.skipUnless
  unittest0.skip
except AttributeError:
  import unittest2 as unittest
else:
  unittest = unittest0
del unittest0

IGNORE_DIRECTORIES = set (['.svn', "build", "dist"])

def add_tests_from_directory (suite, directory):
  skipped_modules = []
  print ("Adding tests from ", directory)
  for filepath in glob.glob (os.path.join (directory, "test_*.py")):
    module_name = os.path.basename (filepath).split (".")[0]
    try:
      pymodule = imp.load_source (module_name, filepath)
    except RuntimeError, err:
      skipped_modules.append (module_name)
      continue
    else:
      for item in dir (pymodule):
        obj = getattr (pymodule, item)
        if isinstance (obj, type) and issubclass (obj, unittest.TestCase):
          suite.addTest (unittest.TestLoader ().loadTestsFromTestCase (obj))
  if skipped_modules:
    print "Skipped because not running as Admin:"
    for m in skipped_modules:
      print "  ", m

def main (test_directory="."):
  suite = unittest.TestSuite ()
  add_tests_from_directory (suite, test_directory)
  for dirpath, dirnames, filenames in os.walk (test_directory):
    dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRECTORIES]
    for dirname in dirnames:
      add_tests_from_directory (suite, os.path.join (dirpath, dirname))

  unittest.TextTestRunner (verbosity=2).run (suite)

if __name__ == '__main__':
  main (*sys.argv[1:])
