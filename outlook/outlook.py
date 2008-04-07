import os, sys

import win32com.client

class Folder (object):
  def __init__ (self, folder):
    self._folder = folder
  def __getattr__ (self, attribute):
    return getattr (self._folder, attribute)
  def __iter__ (self):
    #
    # NB You *must* collect a reference to the
    # Messages collection here; otherwise GetFirst/Next
    # resets every time.
    #
    messages = self._folder.Messages
    message = messages.GetFirst ()
    while message:
      yield message
      message = messages.GetNext ()
      
session = win32com.client.gencache.EnsureDispatch ("MAPI.Session")
session.Logon ("Outlook")

inbox = Folder (session.Inbox)
