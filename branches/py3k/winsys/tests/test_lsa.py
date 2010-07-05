import os, sys
import unittest

from winsys import _lsa

class TestLSA (unittest.TestCase):

  def test_LSA_logon_sessions (self):
    for logon_session in _lsa.LSA.logon_sessions ():
      logon_session.dump ()

if __name__ == "__main__":
  unittest.main ()
  if sys.stdout.isatty (): raw_input ("Press enter...")
