import os

import win32file
import win32event
import win32con

def watch (path_to_watch, hEvent):
  #
  # FindFirstChangeNotification sets up a handle for watching
  #  file changes. The first parameter is the path to be
  #  watched; the second is a boolean indicating whether the
  #  directories underneath the one specified are to be watched;
  #  the third is a list of flags as to what kind of changes to
  #  watch for. We're just looking at file additions / deletions.
  #
  hChange = win32file.FindFirstChangeNotification (
    path_to_watch,
    0,
    win32con.FILE_NOTIFY_CHANGE_FILE_NAME
  )

  #
  # Loop forever, listing any file changes. The WaitFor... will
  #  time out every half a second allowing for keyboard interrupts
  #  to terminate the loop.
  #
  try:

    while 1:
      result = win32event.WaitForMultipleObjects ([hEvent, hChange], 0, 500)

      #
      # If the WaitFor... returned because of a notification (as
      #  opposed to timing out or some error) then look for the
      #  changes in the directory contents.
      #
      
      if result == win32con.WAIT_OBJECT_0:
        break
      elif result == win32con.WAIT_OBJECT_0 + 1:
        win32event.PulseEvent (hEvent)
        win32file.FindNextChangeNotification (hChange)

  finally:
    win32file.FindCloseChangeNotification (hChange)
