import os, sys
import _winreg

import win32com.client
import winerror
from pywintypes import com_error

#
# Do enough to ensure constants are available
#
win32com.client.gencache.EnsureDispatch ("MAPI.Session")
constants = win32com.client.constants

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
      
def session (profile="", fallback_to_dialog=1):
  """session - return a logged-on CDO session.

  profile - name of a predefined profile
  fallback_to_dialog - if unable to connect to an
   active session, present the profile-selection dialog

  Return: a logged-on session

  If the profile is given (typically from default_profile ()
   below) a new session is created from that profile. If
   the profile is not passed -- the default -- an
   attempt is made to attach to an existing session,
   falling back by default to presenting the dialog
   box of possible profiles if no session is active.

  eg
  import outlook
  session = outlook.session (cdo.default_profile ())

  or

  import outlook
  session = outlook.session ()
  """
  _session = win32com.client.gencache.EnsureDispatch ("MAPI.Session")

  #
  # If a profile is specified, use that; if not,
  #  attempt to hook into an existing session. If
  #  there isn't one, the system will fall back on
  #  displaying a dialog box.
  #
  if profile:
    _session.Logon (ProfileName=profile, NewSession=1)
  else:
    _session.Logon (NewSession=0, ShowDialog=fallback_to_dialog)
  return _session

def temporary_session (exchange_server, mailbox_name):
  """Create a temporary session. For me, the mailbox name
   is tim.golden - not sure how it's determined.
  """
  _session = win32com.client.gencache.EnsureDispatch ("MAPI.Session")
  _session.Logon (ProfileInfo="%s\n%s" % (exchange_server, mailbox_name))
  return _session

def default_profile ():
  """default profile - poke around in the registry to find the
   user's default profile.

  Return the user's default profile or a blank string
  """
  HKCU = _winreg.HKEY_CURRENT_USER
  try:
    hProfiles = _winreg.OpenKey (
      HKCU, 
      r"Software\Microsoft\Windows NT\CurrentVersion\Windows Messaging Subsystem\Profiles"
    )
    value, _ = _winreg.QueryValueEx (hProfiles, "DefaultProfile")
    return value
  except WindowsError, (errno, errmsg):
    if errno <> winerror.ERROR_FILE_NOT_FOUND:
      raise
  
  try:
    hProfiles = _winreg.OpenKey (
      HKCU, 
      r"Software\Microsoft\Windows Messaging Subsystem\Profiles"
    )
    value, _ = _winreg.QueryValueEx (hProfiles, "DefaultProfile")
    return value
  except WindowsError, (errno, errmsg):
    if errno <> winerror.ERROR_FILE_NOT_FOUND:
      raise
  
  return ""

def inbox (session_to_use=None):
  return Folder (session (session_to_use).Inbox)

def send (session, recipients, subject, message_text, attachments=[], sender=None):
  """send - send an email to a list of recipients, optionally
   adding attachments. This is supposed to mirror the same
   function in smtpmail.

   session - a logged-on CDO session
   recipients - either a comma-separated list of recipients or a
    Python list of recipients
   subject
   message_text
   attachments
  """
  message = session.Outbox.Messages.Add ()
  message.Subject = subject
  message.Text = message_text
  
  if sender:
    message.Sender.Name = sender

  #
  # Convert comma-separated string to true
  #  list if necessary.
  #
  if type (recipients) == type (""):
    recipients = recipients.split (",")
  for recipient in recipients:
    message_recipient = message.Recipients.Add ()
    message_recipient.Name = recipient
    message_recipient.Resolve ()

  #
  # Convert one attachment to a list of
  #  one if necessary.
  #
  if type (attachments) <> type ([]):
    attachments = [attachments]
  for filename in attachments:
    message.Attachments.Add (Name=filename, Type=win32com.client.constants.CdoFileData, Source=filename)

  message.Send ()
