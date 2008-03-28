import os, sys
import contextlib
import fnmatch
import operator
import re

import win32security
import ntsecuritycon
from win32security import *
import win32api
import pywintypes

PySID = pywintypes.SIDType
PyHANDLE = pywintypes.HANDLEType

class x_security (Exception):
  pass

class x_access_denied (x_security):
  pass

def _set (object, attribute, value=None):
  object.__dict__[attribute] = value

def mask_as_string (mask, length=32):
  return "".join ("01"[bool (mask & (2 << i))] for i in range (length)[::-1])
    
def mask_as_list (mask, length=32):
  return [i for i in range (length) if ((2 << i) & mask)]

class Constants (dict):

  def __getattr__ (self, attribute):
    return self[attribute]
  
  @classmethod
  def from_list (cls, keys, namespace=win32security):
    return cls ((key, getattr (namespace, key)) for key in keys)

  @classmethod
  def from_pattern (cls, pattern="*", excluded=[], namespace=win32security):
    return cls.from_list ((key for key in dir (namespace) if fnmatch.fnmatch (key, pattern) and key not in excluded), namespace)
    
  def names (self, patterns=["*"]):
    """From a list of patterns, return the matching names from the
    list of constants. A single string is considered as though a
    list of one.
    """
    if isinstance (patterns, basestring):
      patterns = [patterns]
    for name in self.keys ():
      for pattern in patterns:
        if fnmatch.fnmatch (name, pattern):
          yield name
  
  def names_from_value (self, value, patterns=["*"]):
    """From a number representing the or-ing of several integer values,
    work out which of the constants make up the number using the pattern
    to filter the "classes" or constants present in the dataset.
    """
    return [name for name in self.names (patterns) if value & self[name]]
    
  def name_from_value (self, value, patterns=["*"]):
    for name in self.names (patterns):
      if self[name] == value:
        return name
    else:
      raise KeyError, "No constant matching name %s and value %d" % (patterns, value)

ACE_FLAGS = Constants.from_list (["CONTAINER_INHERIT_ACE", "INHERIT_ONLY_ACE", "INHERITED_ACE", "NO_PROPAGATE_INHERIT_ACE", "OBJECT_INHERIT_ACE"])
ACE_TYPES = Constants.from_pattern ("*_ACE_TYPE")
DACE_TYPES = Constants.from_pattern ("ACCESS_*_ACE_TYPE")
SACE_TYPES = Constants.from_pattern ("SYSTEM_*_ACE_TYPE")
PRIVILEGE_ATTRIBUTES = Constants.from_pattern ("SE_PRIVILEGE_*")
PRIVILEGES = Constants.from_pattern ("SE_*_NAME")
WELL_KNOWN_SIDS = Constants.from_pattern ("Win*Sid")
SE_OBJECT_TYPE = Constants.from_list ([
  "SE_UNKNOWN_OBJECT_TYPE",
  "SE_FILE_OBJECT",
  "SE_SERVICE",
  "SE_PRINTER",
  "SE_REGISTRY_KEY",
  "SE_LMSHARE",
  "SE_KERNEL_OBJECT",
  "SE_WINDOW_OBJECT",
  "SE_DS_OBJECT",
  "SE_DS_OBJECT_ALL",
  "SE_PROVIDER_DEFINED_OBJECT",
  "SE_WMIGUID_OBJECT",
  "SE_REGISTRY_WOW64_32KEY"
])
SECURITY_INFORMATION = Constants.from_pattern ("*_SECURITY_INFORMATION")

class _SecurityObject (object):
  
  def __init__ (self):
    self._dirty = True
    
  def _update (self):
    self._dirty = False
    
  def __str__ (self):
    self._update ()
    return self.as_string ()
  
  def as_string (self):
    return "<%s>" % self.__class__.__name__
  
  def pyobject (self):
    self._update ()
    return None
    
  def raw (self):
    self._update ()
    return None

_Null = _SecurityObject ()

class Privilege (_SecurityObject):
  
  def __init__ (self, luid, attributes=0):
    """attributes can either be an int (the result of or-ing
    the different attributes you want) or a Python sequence of
    those integers. A luid is a 64-bit integer representing the
    privilege in question.
    """
    _SecurityObject.__init__ (self)
    self.reset (luid, attributes)
    
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

    try:
      self.attributes = reduce (operator.or_, attributes)
    except TypeError:
      try:
        self.attributes = int (attributes)
      except TypeError:
        raise x_security, "Privilege attributes must be sequence or int"
    self._update ()

  def as_string (self):
    return self.name

  @staticmethod
  def from_string (string):
    return Privilege (win32security.LookupPrivilegeValue ("", string))

@contextlib.contextmanager
def impersonate (user, password):
  token = Principal.from_name (user).logon (password).impersonate ()
  yield token
  token.unimpersonate ()
  
@contextlib.contextmanager
def privileges (privileges, token=None):
  if token is None:
    token = Token ()
  token.enable_privileges (privileges)
  yield token
  token.disable_privileges (privileges)

class Token (_SecurityObject):

  TEMPLATE = """User: %(user)s
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
"""
  
  def __init__ (self, hToken = None):
    _SecurityObject.__init__ (self)
    self.reset (hToken)

  def __getattr__ (self, key):
    return self._info[key]
  
  def as_string (self):
    return self.TEMPLATE % self._info
    
  def __repr__ (self):
    return "<Token: %s>" % self.user
  
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

  def reset (self, hToken):
    if hToken:
      self.hToken = hToken
    else:
      flags = win32security.TOKEN_READ | win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
      self.hToken = self.get_token (flags)
    self._update ()
  
  @staticmethod
  def get_token (flags):
    try:
      return win32security.OpenThreadToken (win32api.GetCurrentThread (), flags, True)
    except win32security.error, (errno, errcontext, errmsg):
      if errno == 1008: 
        return win32security.OpenProcessToken (win32api.GetCurrentProcess (), flags)
      else:
        raise

  def _update (self):
    if self._dirty:
      self._info = {}
      sid, attributes = self.info ("User")
      self._info['user'] = Principal (sid, attributes=attributes)
      self._info['owner'] = Principal (self.info ("Owner"))
      self._info['groups'] = [Principal (sid, attributes=attributes) for sid, attributes in self.info ("Groups")]
      self._info['restricted_sids'] = [Principal (sid, attributes=attributes) for sid, attributes in self.info ("RestrictedSids")]
      self._info['privileges'] = [Privilege (luid, attr) for (luid, attr) in self.info ("Privileges")]
      self._info['primary_group'] = Principal (self.info ("PrimaryGroup"))
      try:
        self._info['source'] = self.info ("Source")
      except x_access_denied:
        self._info['source'] = None
      self._info['default_dacl'] = ACL (self.info ("DefaultDacl"))
      self._info['type'] = self.info ("Type")
      #~ self._info['impersonation_level'] = self.info ("ImpersonationLevel")
      self._info['session_id'] = self.info ("SessionId")
      self._info['statistics'] = self.info ("Statistics")
      _SecurityObject._update (self)
    
  def enable_privileges (self, privileges):
    privs_to_enable = []
    if isinstance (privileges, basestring):
      privileges = [privileges]
    for priv in privileges:
      try:
        privs_to_enable.append ((int (priv), const.SE_PRIVILEGE_ENABLED))
      except ValueError:
        privs_to_enable.append ((Privilege.from_string (priv).luid, const.SE_PRIVILEGE_ENABLED))
    win32security.AdjustTokenPrivileges (self.hToken, 0, privs_to_enable)
    self._dirty = True

  def disable_privileges (self, privileges):
    privs_to_disable = []
    for priv in privileges:
      try:
        privs_to_disable.append ((int (priv), 0))
      except ValueError:
        privs_to_disable.append ((Privilege.from_string (priv).luid, 0))
    win32security.AdjustTokenPrivileges (self.hToken, 0, privs_to_disable)
    self._dirty = True
    
  def impersonate (self):
    self._update ()
    win32security.ImpersonateLoggedOnUser (self.hToken)
    return self
    
  def unimpersonate (self):
    win32security.RevertToSelf ()

class _SID (_SecurityObject):

  def __init__ (self, sid):
    _SecurityObject.__init__ (self)
    self.reset (sid)

  def __getattr__ (self, attribute):
    self._dirty = True
    return getattr (self._sid, attribute)

  def __len__ (self):
    return self._sid.GetLength ()

  def __eq__ (self, other):
    return self._sid == other._sid
    
  def __repr__ (self):
    return "<_SID: %s>" % self.as_string ()

  def reset (self, sid):
    self._sid = sid
    self._update ()
  
  def pyobject (self):
    return self._sid

  def raw (self):
    return buffer (self._sid)

  def as_string (self):
    return ConvertSidToStringSid (self._sid)
  
  @staticmethod
  def from_string (string):
    return _SID (ConvertStringSidToSid (string))

class Principal (_SecurityObject):

  def __init__ (self, account, system_name=None):
    if isinstance (account, PySID):
      account = _SID (account)
    
    if account is None:
      self.name = self.sid = self.domain = self.type = None
    elif isinstance (account, _SID):
      self.sid = account
      self.name, self.domain, self.type = win32security.LookupAccountSid (system_name, self.sid.pyobject ())
    elif isinstance (account, basestring):
      self.name = account.split ("\\", 1)[-1]
      self.sid, self.domain, self.type = win32security.LookupAccountName (system_name, account)
    else:
      raise x_security, "Principal must be a SID or a name"

  def __repr__ (self):
    return r"<Principal: %s [%s]>" % (self, self.sid)

  def pyobject (self):
    return self.sid.pyobject ()
  
  def as_string (self):
    if self.domain:
      return r"%s\%s" % (self.domain, self.name)
    else:
      return self.name or str (self.sid)
      
  def logon (self, password):
    hUser = win32security.LogonUser (
      self.name,
      self.domain,
      password,
      win32security.LOGON32_LOGON_NETWORK,
      win32security.LOGON32_PROVIDER_DEFAULT
    )
    return Token (hUser)
  
  @classmethod
  def from_well_known (cls, well_known, domain_name=None):
    if domain_name:
      domain_sid = cls.from_name (domain_name).pyobject ()
    else:
      domain_sid = None
    return cls (win32security.CreateWellKnownSid (well_known, domain_sid))
    
class ACE (_SecurityObject):

  ACE_FLAGS = ["CONTAINER_INHERIT_ACE", "INHERIT_ONLY_ACE", "INHERITED_ACE", "NO_PROPAGATE_INHERIT_ACE", "OBJECT_INHERIT_ACE"]
  
  def __init__ (self, type, trustee, access, flags=0, object_type=None, inherited_object_type=None):
    """Construct a new ACE
    
    @param type String or number representing one of the *_ACE_TYPE constants
    @param trustee "domain\user" or Principal instance representing the security principal
    @param access Bitmask
    @param flags Bitmask or Set of strings or numbers representing the AceFlags constants
    """
    _SecurityObject.__init__ (self)
    self.reset (type, trustee, access, flags)

  def __getattr__ (self, attribute):
    return getattr (self._ace, attribute)

  def __eq__ (self, other):
    return self._ace == other._ace
  
  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.as_tuple ())
    
  def pyobject (self):
    return self._ace
  
  @staticmethod
  def from_ace (ace):
    (type, flags) = ace[0]
    name = const.name_from_value (type, ["ACCESS_*_ACE_TYPE", "SYSTEM_*_ACE_TYPE"])
    if "object" in name.lower ().split ("_"):
      mask, object_type, inherited_object_type, sid = ace[1:]
    else:
      mask, sid = ace[1:]
      object_type = inherited_object_type = None
    
    if name not in const.names ("ACCESS_*_ACE_TYPE"):
      return DACE (type, Principal (sid), mask, flags, object_type, inherited_object_type)
    else:
      return SACE (type, Principal (sid), mask, flags, object_type, inherited_object_type)
  
  def as_tuple (self):
    return self.type, self.trustee, self.access, self.flags
  
  def as_string (self):
    type = const.name_from_value (self.type, "ACCESS_*_ACE_TYPE")
    flags = " | ".join (const.names_from_value (self.flags, self.ACE_FLAGS))
    access = " | ".join (const.names_from_value (self.access, "FILE_*"))
    #~ access = ", ".join (str (i) for i in mask_as_list (self.access))
    return "%s %s %s %s" % (type, self.trustee, access, flags)
  
  def reset (self, type, trustee, access, flags):
    self.type = type
    self.trustee = trustee
    self.access = access
    try:
      self.flags = int (flags)
    except TypeError:
      self.flags = reduce (operator.or_, flags)
    self._update ()
    
class DACE (ACE):
  pass
  
class SACE (ACE):
  pass

class ACL (_SecurityObject):
  
  _ACE = ACE
  
  def __init__ (self, acl):
    _SecurityObject.__init__ (self)
    self.reset (acl)

  def __getattr__ (self, attribute):
    return getattr (self._acl, attribute)

  def __len__ (self):
    return self._acl.GetAceCount ()

  def __iter__ (self):
    for i in range (len (self)):
      yield self[i]
    
  def __getitem__ (self, index):
    if index < 0:
      index = self._acl.GetAceCount () + index
      print "index < 0; using", index
    return self._ACE.from_ace (self._acl.GetAce (index))
    
  def __delitem__ (self, index):
    if index < 0:
      index = self._acl.GetAceCount () + index
    self._acl.DeleteAce (index)
    
  def append (self, ace):
    if ace.ace_type == ACE_TYPES.ACCESS_ALLOWED:
      self._acl.AddAccessAllowedAce (win32security.ACL_REVISION, ace.access, ace.sid.pyobject ())
    elif ace.ace_type == ACE_TYPES.ACCESS_DENIED:
      self._acl.AddAccessDeniedAce (win32security.ACL_REVISION, ace.access, ace.sid.pyobject ())
      
  def pop (self):
    ace = self[-1]
    del self[-1]
    return ace

  def reset (self, acl):
    self._acl = acl
    self._update ()
  
  def as_string (self):
    return "\n".join (str (ace) for (i, ace) in enumerate (self))
        
  def pyobject (self):
    return self._acl

  def raw (self):
    return buffer (self._acl)
    
class DACL (ACL):
  _ACE = DACE
  
class SACL (ACL):
  _ACE = SACE

#
# General policy: store as security.* objects rather
# than as raw pywin32 objects.
#
class Security (_SecurityObject):

  DEFAULT_SECURITY_INFORMATION = \
    SECURITY_INFORMATION.OWNER_SECURITY_INFORMATION | \
    SECURITY_INFORMATION.GROUP_SECURITY_INFORMATION | \
    SECURITY_INFORMATION.DACL_SECURITY_INFORMATION    
  
  def __init__ (
    self, 
    object=None,
    object_type=SE_OBJECT_TYPE.SE_FILE_OBJECT, 
    options=DEFAULT_SECURITY_INFORMATION,
    inherit_handle=True
  ):
    """
    @param object The name or the handle of the object whose security is to be retrieved
    @param type One of the SE_OBJECT_TYPE enumeration
    @param options A bitmask formed by combining the appropriate *_SECURITY_INFORMATION
    constants. NB The SACL usually needs the SE_SECURITY_NAME privilege
    enabled. For this reason it is not included in the defaults.
    """
    _SecurityObject.__init__ (self)
    self._sa = win32security.SECURITY_ATTRIBUTES ()
    if object is None:
      self.owner = None
      self.group = None
      self.dacl = None
      self.sacl = None
      self.inherit_handle = None
    else:
      if isinstance (object, PyHANDLE):
        sd = GetSecurityInfo (object, object_type, options)
      else:
        sd = GetNamedSecurityInfo (object, object_type, options)      
      self.owner = Principal (sd.GetSecurityDescriptorOwner ())
      self.group = Principal (sd.GetSecurityDescriptorGroup ())
      self.dacl = DACL (sd.GetSecurityDescriptorDacl ())
      self.sacl = SACL (sd.GetSecurityDescriptorSacl ())
      self.inherit_handle = inherit_handle
  
  def __repr__ (self):
    self._update ()
    return "<Security: %s>" % win32security.ConvertSecurityDescriptorToStringSecurityDescriptor (
      self.pyobject ().SECURITY_DESCRIPTOR, 
      win32security.SDDL_REVISION_1,
      -1
    )

  def _update (self):
    if self._dirty:
      self._sa.bInheritHandle = self.inherit_handle
      if self.owner:
        self._sa.SetSecurityDescriptorOwner (self.owner.pyobject (), False)
      if self.group:
        self._sa.SetSecurityDescriptorGroup (self.group.pyobject (), False)
      
      #
      # The first & last flags on the Set...acl methods represent,
      # respectively, whether the ACL is present (!) and whether
      # it's the result of inheritance.
      #
      if self.dacl:
        self._sa.SetSecurityDescriptorDacl (True, self.dacl.pyobject (), False)
      if self.sacl:
        self._sa.SetSecurityDescriptorSacl (True, self.sacl.pyobject (), False)
    self._dirty = False

  def pyobject (self):
    self._update ()
    return self._sa
    
  @classmethod
  def from_security_descriptor (cls, sd, inherit_handle=True):
    """Factory method to construct a Security object from a PySECURITY_DESCRIPTOR 
    object.
    
    @param sd A PySECURITY_DESCRIPTOR instance
    @param inherit_handle A flag indicating whether the handle is to be inherited
    @return a Security instance
    """
    security = Cls ()
    security.owner = Principal (sd.GetSecurityDescriptorOwner ())
    security.group = Principal (sd.GetSecurityDescriptorGroup ())
    security.dacl = DACL (sd.GetSecurityDescriptorDacl  ())
    security.sacl = SACL (sd.GetSecurityDescriptorSacl ())
    security.inherit_handle = inherit_handle
  
  @classmethod
  def from_string (cls, sddl):
    """Factory method to construct a Security object from a string in
    Microsoft SDDL format.
    
    @param string A string in Microsoft SDDL format
    @return A Security instance
    """
    return cls.from_security_descriptor (
      sd=win32security.ConvertStringSecurityDescriptorToSecurityDescriptor (
        string, 
        win32security.SDDL_REVISION_1
      )
    )

  def as_string (self):
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

if __name__ == '__main__':
  print Token ()
