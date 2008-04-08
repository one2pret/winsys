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

import outlook
import watch_dir

MONITOR_FLAG = "monitor-outlook"
SLEEP_FOR_SECS = 10
REACTORS_DIR = os.path.join (os.path.dirname (sys.modules[__name__].__file__), "reactors")

def set_read (message):
  message.Unread = False

def reload_reactors ():
  print "Reloading reactors"
  reactors = []
  for pyfile in glob.glob (os.path.join (REACTORS_DIR, "*.py")):
    module_name = os.path.basename (pyfile).split (".")[0]
    print "Loading reactor:", module_name
    pymodule = imp.load_source (module_name, pyfile)
    reactors.append ((re.compile (pymodule.message_filter or ""), pymodule.process_message))
  return reactors
  
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
            print "Processing:", message.Subject
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
  session = outlook.session ()
  main (session)
