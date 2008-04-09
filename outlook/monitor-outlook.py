"""Track incoming emails and take action according to clues in
the subject, body etc.
"""
import os, sys
import glob
import imp
import re
import threading
import time

import win32con
import win32event

import topological_sort
import outlook
import watch_dir

MONITOR_FLAG = "monitor-outlook"
SLEEP_FOR_SECS = 10
REACTORS_DIR = os.path.join (os.path.dirname (sys.modules[__name__].__file__), "reactors")

class Reactor (object):
  
  def __init__ (self, name, module):
    self.name = name
    self.process_message = getattr (module, "process_message")
    self.filter = re.compile (getattr (module, "message_filter", "") or "")
    self.depends_on = getattr (module, "depends_on", []) or []

def reload_reactors ():
  print
  print "Reloading reactors at", time.asctime ()
  reactors = {}
  orderings = []
  for pyfile in sorted (glob.glob (os.path.join (REACTORS_DIR, "*.py"))):
    module_name = os.path.basename (pyfile).split (".")[0]
    pymodule = imp.load_source (module_name, pyfile)
    reactors[module_name] = Reactor (module_name, pymodule)
  
  dependencies = []
  for reactor in reactors.values ():
    for must_run_first in reactor.depends_on:
      dependencies.append ((reactors[must_run_first], reactor))
  sorted_reactors = topological_sort.topological_sort (reactors.values (), orderings)
  for reactor in sorted_reactors:
    print "  ", reactor.name
  return [(r.filter, r.process_message) for r in sorted_reactors]

def is_message_flagged (message):
  return message.Categories and MONITOR_FLAG in message.Categories

def flag_message (message):
  categories = set (message.Categories or ())
  categories.add (MONITOR_FLAG)
  message.Categories = tuple (categories)

def unflag_message (message):
  message.Categories = tuple (c for c in (message.Categories or ()) if c <> MONITOR_FLAG)

def main (session):
  reactors = reload_reactors ()
  hEvent = win32event.CreateEvent (None, 0, 0, "monitor-outlook")
  threading.Thread (target=watch_dir.watch, args=(REACTORS_DIR, hEvent)).start ()
  try:
    inbox = outlook.inbox (session)

    try:
      while True:
        for message in inbox:
          if message.Unread and not is_message_flagged (message):
            print "Processing:", message.Subject, "at", time.asctime ()
            for filter, reactor in reactors:
              if filter.search (message.Subject):
                if reactor (message):
                  break
            flag_message (message)
            message.Update ()

        result = win32event.WaitForSingleObject (hEvent, 1000 * SLEEP_FOR_SECS)
        if result == win32con.WAIT_OBJECT_0:
          reactors = reload_reactors ()
    
    except KeyboardInterrupt:
      pass
        
  finally:
    win32event.PulseEvent (hEvent)

if __name__ == '__main__':
  session = outlook.session (outlook.default_profile ())
  main (session)
