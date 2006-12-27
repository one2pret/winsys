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

def _set (object, attribute, value=None):
  object.__dict__[attribute] = value

def mask_as_string (mask, length=32):
  return "".join ("01"[bool (mask & (2 << i))] for i in range (length)[::-1])

class Privilege (object):
  
  ATTRIBUTES = ["enabled", "enabled_by_default", "used_for_access"]
  
  def __init__ (self, luid, attributes=None):
    self.reset (luid, attributes)
    
  def __str__ (self):
    return self.as_string ()
    
  def __repr__ (self):
    return "<Privilege: %s (%s)>" % (self.name, self.luid)
    
  def reset (self, luid, attributes):
    self.luid = luid
    try:
      self.name = win32security.LookupPrivilegeName ("", self.luid)
      self.description = win32security.LookupPrivilegeDisplayName ("", self.name)
    except win32security.error, (errno, errctx, errmsg):
      if errno == 1313:
        self.name = self.description = "<Unknown>"
      else:
        raise
    
    self.attributes = set (a for a in self.ATTRIBUTES if (attributes or 0) & getattr (win32security, "SE_PRIVILEGE_" + a.upper ()))

  def as_string (self):
    return self.name
    
  @staticmethod
  def from_string (string):
    return Privilege (win32security.LookupPrivilegeValue ("", string))

class Token (object):

  def __init__ (self, hToken = None):
    if hToken:
      self.hToken = hToken
    else:
      flags = win32security.TOKEN_READ
      try:
        self.hToken = win32security.OpenThreadToken (win32api.GetCurrentThread (), flags, True)
      except win32security.error, (errno, errcontext, errmsg):
        if errno == 1008: 
          self.hToken = win32security.OpenProcessToken (win32api.GetCurrentProcess (), flags)
        else:
          raise
    self.reset ()

  def __getattr__ (self, key):
    return self._info[key]
  
  def __str__ (self):
    return self.as_string ()
  
  def as_string (self):
    return """
User: %(user)s
Owner: %(owner)s
Groups: %(groups)s
Restricted SIDs: %(restricted_sids)s
Privileges: %(privileges)s
Primary Group: %(primary_group)s
Source: %(source)s
Default DACL: %(default_dacl)s
Type: %(type)s
Session ID: %(session_id)s
Statistics: %(statistics)s
""" % self._info
  
  def info (self, type):
    try:
      info_type = int (type)
    except ValueError:
      info_type = getattr (win32security, "Token" + type)
    try:
      return win32security.GetTokenInformation (self.hToken, info_type)
    except win32security.error, (errno, context, errmsg):
      if errno == 5:
        raise x_access_denied (repr (self), type)
      else:
        raise

  def reset (self):
    self._info = {}
    sid, attributes = self.info ("User")
    self._info['user'] = Account (sid, attributes=attributes)
    self._info['owner'] = Account (self.info ("Owner"))
    self._info['groups'] = [Account (sid, attributes=attributes) for sid, attributes in self.info ("Groups")]
    self._info['restricted_sids'] = [Account (sid, attributes=attributes) for sid, attributes in self.info ("RestrictedSids")]
    self._info['privileges'] = [Privilege (luid, attr) for (luid, attr) in self.info ("Privileges")]
    self._info['primary_group'] = Account (self.info ("PrimaryGroup"))
    try:
      self._info['source'] = self.info ("Source")
    except x_access_denied:
      self._info['source'] = None
    self._info['default_dacl'] = ACL (self.info ("DefaultDacl"))
    self._info['type'] = self.info ("Type")
    ## FIXME self._info['impersonation_level'] = self.info ("ImpersonationLevel")
    self._info['session_id'] = self.info ("SessionId")
    self._info['statistics'] = self.info ("Statistics")
    
  def enable_privileges (self, privileges):
    privs_to_enable = []
    for priv in privilege:
      try:
        privs_to_enable.append (int (priv), win32security.SE_PRIVILEGE_ENABLED)
      except ValueError:
        privs_to_enable.append (Privilege.from_string (priv).luid, win32security.SE_PRIVILEGE_ENABLED)
    win32security.AdjustTokenPrivileges (self.hToken, 0, privs_to_enable)

  def disable_privileges (self, privileges):
    privs_to_enable = []
    for priv in privilege:
      try:
        privs_to_enable.append (int (priv), 0)
      except ValueError:
        privs_to_enable.append (Privilege.from_string (priv).luid, 0)
    win32security.AdjustTokenPrivileges (self.hToken, 0, privs_to_enable)

class SID (object):

  def __init__ (self, sid):
    self._sid = sid

  def __str__ (self):
    return ConvertSidToStringSid (self._sid)

  def __getattr__ (self, attribute):
    return getattr (self._sid, attribute)

  def __len__ (self):
    return self._sid.GetLength ()

  def __eq__ (self, other):
    return self._sid == other._sid

  def pyobject (self):
    return self._sid

  def raw (self):
    return buffer (self._sid)

  @staticmethod
  def from_string (string):
    return SID (ConvertStringSidToSid (string))

class Account (object):

  def __init__ (self, sid, system_name="", attributes=None):
    self.sid = SID (sid)
    self.attributes = attributes
    try:
      self.name, self.domain, self.type = win32security.LookupAccountSid (system_name, sid)
    except win32security.error, (errno, context, errmsg):
      self.name = self.domain = ""
      self.type = None

  def __str__ (self):
    return self.as_string ()

  def __repr__ (self):
    return r"<Account: %s [%s]>" % (self, self.sid)

  def as_string (self):
    if self.domain:
      return r"%s\%s" % (self.domain, self.name)
    else:
      return self.name or str (self.sid)
  
  @staticmethod
  def from_name (account_name, system_name=""):
    sid, domain, type = win32security.LookupAccountName (system_name, account_name)
    return Account (sid, domain)
    
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
    self._ace = ace
    self.reset ()

  def __getattr__ (self, attribute):
    return getattr (self._ace, attribute)

  def __eq__ (self, other):
    return self._ace == other._ace
  
  def __repr__ (self):
    return "<ACE: %s>" % (self.as_tuple (),)
  
  def __str__ (self):
    return self.as_string ()

  def as_tuple (self):
    return self.type, self.account, self.mask
  
  def as_string (self):
    if "Allowed" in self.type:
      access = "permit"
    elif "Denied" in self.type:
      access = "forbid"
    elif "Audit" in self.type:
      access = "audit"
    else:
      access = "<unknown>"
    trustee = self.account
    rights = mask_as_string (self.mask)
    return "%s %s %s" % (access, trustee, rights)
  
  def reset (self):
    (type, flags) = self._ace[0]
    if type in [win32security.ACCESS_ALLOWED_ACE_TYPE, win32security.ACCESS_DENIED_ACE_TYPE, win32security.SYSTEM_AUDIT_ACE_TYPE]:
      mask, sid = self._ace[1:]
    else:
      mask, object_type, inherited_object_type, sid = self._ace[1:]

    _set (self, "type", self.TYPES[type])
    _set (self, "mask", mask)
    _set (self, "account", Account (sid))

class ACL (object):
  
  def __init__ (self, acl):
    self._acl = acl

  def __getattr__ (self, attribute):
    return getattr (self._acl, attribute)

  def __len__ (self):
    return self._acl.GetAceCount ()

  def __iter__ (self):
    for i in range (len (self)):
      yield self[i]
    
  def __getitem__ (self, key):
    return ACE (self._acl.GetAce (key))

  def __str__ (self):
    return self.as_string ()
  
  def as_string (self):
    return "\n".join (str (ace) for (i, ace) in enumerate (self))
        
  def pyobject (self):
    return self._acl

  def raw (self):
    return buffer (self._acl)  

class Security (object):

  def __init__ (self, sd=None):
    self.reset (sd)

  def reset (self, sd):
    self._sd = sd
    if sd.GetSecurityDescriptorOwner ():
      self.owner = Account (sid=sd.GetSecurityDescriptorOwner ())
    else:
      self.owner = None
    if sd.GetSecurityDescriptorGroup ():
      self.group = Account (sid=sd.GetSecurityDescriptorGroup ())
    else:
      self.group = None
    if sd.GetSecurityDescriptorDacl ():
      self.dacl = ACL (sd.GetSecurityDescriptorDacl ())
    else:
      self.dacl = None
    if sd.GetSecurityDescriptorSacl ():
      self.sacl = ACL (sd.GetSecurityDescriptorSacl ())
    else:
      self.sacl = None

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
    def acl_as_string (acl, indent="  "):
      if acl:
        return ("\n" + indent).join (str (acl).splitlines ())
      else:
        return indent + "<Unknown>"
    return """%s
Owner: %s
Group: %s
DACL: 
  %s
SACL: 
%s""" % (
  repr (self), 
  self.owner or "<Unknown>", 
  self.group or "<Unknown>", 
  acl_as_string (self.dacl) or "<Unknown>", 
  acl_as_string (self.sacl) or "<Unknown>"
)

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
