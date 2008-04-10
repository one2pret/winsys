"""Track incoming emails and take action according to clues in
the subject, body etc.
"""
import os, sys
import glob
import imp
import re
import threading
import time
import traceback

import win32con
import win32event
import win32file

import topological_sort
import outlook
import watch_dir

MONITOR_FLAG = "monitor-outlook"
SLEEP_FOR_SECS = 10
REACTORS_DIR = os.path.join (os.path.dirname (sys.modules[__name__].__file__), "reactors")

def get_real_com_errno (error_info):
  hresult_code, hresult_name, additional_info, parameter_in_error = error_info
  if additional_info:
    wcode, source_of_error, error_description, whlp_file, whlp_context, scode = additional_info
    return scode
  else:
    return None
  
class Reactor (object):
  
  def __init__ (self, name, module):
    self.name = name
    self.process_message = getattr (module, "process_message")
    self.filter = re.compile (getattr (module, "message_filter", "") or "")
    self.depends_on = getattr (module, "depends_on", []) or []
    
    init = getattr (module, "init", None)
    if init:
      init ()

def reload_reactors ():
  print
  print "Reloading reactors at", time.asctime ()
  reactors = {}
  for pyfile in sorted (glob.glob (os.path.join (REACTORS_DIR, "*.py"))):
    if not (win32file.GetFileAttributes (pyfile) & win32file.FILE_ATTRIBUTE_HIDDEN):
      module_name = os.path.basename (pyfile).split (".")[0]
      try:
        pymodule = imp.load_source (module_name, pyfile)
        reactors[module_name] = Reactor (module_name, pymodule)
      except:
        print "  *** UNABLE TO LOAD", module_name, "***"
        traceback.print_exc ()
  
  dependencies = []
  for reactor in reactors.values ():
    for must_run_first in reactor.depends_on:
      dependencies.append ((reactors[must_run_first], reactor))
  sorted_reactors = list (topological_sort.sort (reactors.values (), dependencies))
  for reactor in sorted_reactors:
    print "  ", reactor.name
  return [(r.filter, r.process_message) for r in sorted_reactors]

def is_message_flagged (message):
  try:
    value = message.Fields[MONITOR_FLAG]
  except outlook.com_error, error_info:
    if get_real_com_errno (error_info) == -2147221233:
      return False
    else:
      raise
  else:
    return value

def flag_message (message, setting=True):
  if is_message_flagged (message):
    message.Fields[MONITOR_FLAG] = setting
  else:
    message.Fields.Add (MONITOR_FLAG, outlook.constants.vbBoolean, setting)

def unflag_message (message):
  flag_message (message, False)

def main (session):
  inbox = outlook.inbox (session)
  reactors = reload_reactors ()
  
  hEvent = win32event.CreateEvent (None, 0, 0, "monitor-outlook")
  threading.Thread (target=watch_dir.watch, args=(REACTORS_DIR, hEvent)).start ()
  try:
    try:
      while True:
        for message in inbox:
          if message.Unread and not is_message_flagged (message):
            print "Processing:", message.Subject[:80], "at", time.asctime ()
            for filter, reactor in reactors:
              if filter.search (message.Subject):
                reactor (message)
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
