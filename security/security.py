import os, sys
import win32security
from win32security import *
import win32con
import win32api
from ntsecuritycon import *
import pywintypes

PyHANDLE = type (pywintypes.HANDLE ())

class x_access_denied (Exception):
  pass

def set (object, attribute, value=None):
  object.__dict__[attribute] = value

def mask_as_string (mask, length=32):
  return "".join ("01"[bool (mask & (2 << i))] for i in range (length)[::-1])

class ACE (object):

  TYPES = {
    win32security.ACCESS_ALLOWED_ACE_TYPE : "Access Allowed",
    win32security.ACCESS_DENIED_ACE_TYPE : "Access Denied",
    win32security.SYSTEM_AUDIT_ACE_TYPE : "System Audit",
    win32security.ACCESS_ALLOWED_OBJECT_ACE_TYPE : "Access Allowed",
    win32security.ACCESS_DENIED_OBJECT_ACE_TYPE : "Access Denied",
    win32security.SYSTEM_AUDIT_OBJECT_ACE_TYPE : "System Audit",
  }

  def __init__ (self, ace):
    set (self, "_ace", ace)
    set (self, "type")
    set (self, "mask")
    set (self, "account")
    self.reset ()

  def __getattr__ (self, attribute):
    return getattr (self._ace, attribute)

  def __setattr__ (self, attribute, value):
    return setattr (self._ace, attribute, value)

  def __eq__ (self, other):
    return self._ace == other._ace

  def __str__ (self):
    return "%s %s %s" % (self.account, self.type, ", ".join (str (i) for i in range (32) if self.mask & 2 << i))

  def reset (self):
    (type, flags) = self._ace[0]
    if type in [win32security.ACCESS_ALLOWED_ACE_TYPE, win32security.ACCESS_DENIED_ACE_TYPE, win32security.SYSTEM_AUDIT_ACE_TYPE]:
      mask, sid = self._ace[1:]
    else:
      mask, object_type, inherited_object_type, sid = self._ace[1:]

    set (self, "type", self.TYPES[type])
    set (self, "mask", mask)
    set (self, "account", Account (sid))

class ACL (object):

  def __init__ (self, acl):
    set (self, "_acl", acl)

  def __getattr__ (self, attribute):
    return getattr (self._acl, attribute)

  def __setattr__ (self, attribute, value):
    return setattr (self._acl, attribute, value)

  def __len__ (self):
    return self._acl.GetAceCount ()

  def __getitem__ (self, key):
    return ACE (self._acl.GetAce (key))

  def pyobject (self):
    return self._acl

  def raw (self):
    return buffer (self._acl)

class Token (object):

  def __init__ (self, hToken = None):
    if hToken:
      self.hToken = hToken
    else:
      flags = win32security.TOKEN_ALL_ACCESS
      hProcess = win32api.GetCurrentProcess ()
      self.hToken = win32security.OpenProcessToken (hProcess, flags)
    self.reset ()

  def info (self, type):
    try:
      info_type = int (type)
    except ValueError:
      if type.isupper () or type.islower ():
        type = type.title ()
      info_type = getattr (win32security, "Token" + type)
    try:
      return win32security.GetTokenInformation (self.hToken, info_type)
    except win32security.error, (errno, context, errmsg):
      if errno == 5:
        raise x_access_denied (repr (self), type)
      else:
        raise

  def reset (self):
    sid, attributes = self.info ("user")
    self.user = Account (sid, attributes=attributes)
    self.owner = Account (self.info ("owner"))
    self.groups = []
    self.groups = [Account (sid, attributes=attributes) for sid, attributes in self.info ("groups")]
    self.restricted_sids = [Account (sid, attributes=attributes) for sid, attributes in self.info ("RestrictedSids")]
    self.privileges = self.info ("privileges")
    self.primary_group = self.info ("PrimaryGroup")
    try:
      self.source = self.info ("source")
    except x_access_denied:
      self.source = None
    self.default_dacl = ACL (self.info ("DefaultDacl"))
    self.type = self.info ("type")
    ## FIXME self.impersonation_level = self.info ("ImpersonationLevel")
    self.session_id = self.info ("SessionId")
    self.statistics = self.info ("statistics")

class SID (object):

  def __init__ (self, sid):
    set (self, "_sid", sid)

  def __str__ (self):
    return ConvertSidToStringSid (self._sid)

  def __getattr__ (self, attribute):
    return getattr (self._sid, attribute)

  def __setattr__ (self, attribute, value):
    return setattr (self._sid, attribute, value)

  def __len__ (self):
    return self._sid.GetLength ()

  def __eq__ (self, other):
    return self._sid == other._sid

  def pyobject (self):
    return self._sid

  def raw (self):
    return buffer (self._sid)

  @staticmethod
  def from_string (self, string):
    return SID (ConvertStringSidToSid (string))

class Account (object):

  def __init__ (self, sid, domain="", attributes=None):
    self.sid = SID (sid)
    self.attributes = attributes
    try:
      self.name, self.domain, self.type = win32security.LookupAccountSid (domain, sid)
    except win32security.error, (errno, context, errmsg):
      self.name = self.domain = ""
      self.type = None

  def __str__ (self):
    return r"%s\%s" % (self.domain, self.name)

  def __repr__ (self):
    return r"<%s\%s [%s]>" % (self.domain, self.name, self.sid)

  @staticmethod
  def from_name (domain_name, account_name):
    sid, domain, type = win32security.LookupAccountName (domain_name, account_name)
    return Account (sid, domain)

class Security (object):

  def __init__ (self, sd=None):
    self.reset (sd)

  def reset (self, sd):
    self._sd = sd
    self.owner = Account (sid=sd.GetSecurityDescriptorOwner ())
    self.group = Account (sid=sd.GetSecurityDescriptorGroup ())
    self.dacl = ACL (sd.GetSecurityDescriptorDacl ())
    self.sacl = ACL (sd.GetSecurityDescriptorSacl ())

  @staticmethod
  def from_object (object, type="file", options=["owner", "group", "dacl"]):
    """Factory method to create a Security object from an existing Windows object.
    By default this will assume a file object and will attempt to retrieve
    all information.

    @param object The name or the handle of the object whose security is to be retrieved
    @param type Either one of the SE_*_OBJECT constants from win32security or
      a string which represents the central portion of one of those constants
      (eg "file", "pipe", "service")
    @param options Either a bitmask formed by combining the appropriate *_SECURITY_INFORMATION
      constants from win32security, or an iterable of those constants or an
      iterable of strings each representing the first portion of those constants
      (eg "owner", "dacl"). NB The SACL usually needs the SE_SECURITY_NAME privilege
      enabled. For this reason it is not included in the defaults.
    @return a SecurityDescriptor instance
    """
    try:
      object_type = int (type)
    except ValueError:
      object_type = getattr (win32security, "SE_" + type.upper () + "_OBJECT")

    try:
      flags = int (options)
    except (TypeError, ValueError):
      flags = 0
      for option in options:
        try:
          flags |= option
        except TypeError:
          flags |= getattr (win32security, option.upper () + "_SECURITY_INFORMATION")

    if isinstance (object, PyHANDLE):
      return Security (GetSecurityInfo (object, object_type, flags))
    else:
      return Security (GetNamedSecurityInfo (object, object_type, flags))

  def __str__ (self):
    return """%s
      Owner: %s
      Group: %s
      DACL: %s
      SACL: %s
    """ % (repr (self), self.owner or "<Unknown>", self.group or "<Unknown>", self.dacl or "<Unknown>", self.sacl or "<Unknown>")

def adjust_privileges (privilege, enable=True):
  flags = TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
  hToken = win32security.OpenProcessToken (win32api.GetCurrentProcess (), flags)
  privilege_id = win32security.LookupPrivilegeValue (None, privilege)
  if enable:
    new_privileges = [(privilege_id, SE_PRIVILEGE_ENABLED)]
  else:
    new_privileges = [(privilege_id, 0)]
  return win32security.AdjustTokenPrivileges (hToken, 0, new_privileges)

def make_sd ():
  sd = win32security.SECURITY_DESCRIPTOR ()
  sid, domain, account_type = win32security.LookupAccountName ("", "tim")


if __name__ == '__main__':
  adjust_privileges (SE_CHANGE_NOTIFY_NAME)
