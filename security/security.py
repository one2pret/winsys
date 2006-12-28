import os, sys
import win32security
from win32security import *
import win32con
import win32api
from ntsecuritycon import *
import pywintypes

PyHANDLE = type (pywintypes.HANDLE ())

class x_security (Exception):
  pass

class x_access_denied (x_security):
  pass

def _set (object, attribute, value=None):
  object.__dict__[attribute] = value

def mask_as_string (mask, length=32):
  return "".join ("01"[bool (mask & (2 << i))] for i in range (length)[::-1])

def symbol (name, pattern ="%s", namespace=win32security, uppercase=True):
  """Convert a -- possibly lowercase -- string to the corresponding
  numeric constant from a namespace, optionally uppercasing the string
  first. This will typically be used to offer a friendlier list of
  symbols rather than or-ing together long numeric constants. The
  pattern offers a way of prefix/suffixing common constant names.
  
  @param name The symbol whose numeric value is to be returned
  @param pattern A pattern containing a %s which will be replaced by the name
  @param namespace The namespace to be searched
  @param uppercase Should the string be uppercased first?
  @return (name, number) Numeric constant representing the string
  """
  #
  # Check first for the trivial case where a number
  # has been passed. This saves some work when working
  # through a set of values, some or all of which might
  # be numeric.
  #
  try:
    int (name)
  except ValueError:
    if uppercase: name = name.upper ()
    #
    # First try to use the pattern; if that
    # doesn't work, it's possible the caller
    # has passed the full name, so try that.
    #
    try:
      return pattern % name, getattr (namespace, pattern % name)
    except AttributeError:
      return name, getattr (namespace, name)
  else:
    return str (name), name

#
# Example implementation of now-in-2.5 currying
# functionality shamelessly copied from PEP 309.
#
class Partial (object):

  def __init__ (*args, **kw):
    self = args[0]
    self.fn, self.args, self.kw = (args[1], args[2:], kw)

  def __call__ (self, *args, **kw):
    if kw and self.kw:
      d = self.kw.copy ()
      d.update (kw)
    else:
      d = kw or self.kw
    return self.fn (* (self.args + args), **d)
        
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
  
  ATTRIBUTES = ["enabled", "enabled_by_default", "used_for_access"]
  
  def __init__ (self, luid, attributes=None):
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
    
    self.attributes = set (a for a in self.ATTRIBUTES if (attributes or 0) & symbol (a, "SE_PRIVILEGE_%s"))
    self._update ()

  def as_string (self):
    return self.name

  @staticmethod
  def from_string (string):
    return Privilege (win32security.LookupPrivilegeValue ("", string))

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
    if not hToken:
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
          
    self._update ()
    
  def _update (self):
    if self._dirty:
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
      _SecurityObject.update (self)
    
  def enable_privileges (self, privileges):
    privs_to_enable = []
    for priv in privilege:
      try:
        privs_to_enable.append (int (priv), win32security.SE_PRIVILEGE_ENABLED)
      except ValueError:
        privs_to_enable.append (Privilege.from_string (priv).luid, win32security.SE_PRIVILEGE_ENABLED)
    win32security.AdjustTokenPrivileges (self.hToken, 0, privs_to_enable)
    self._dirty = True

  def disable_privileges (self, privileges):
    privs_to_enable = []
    for priv in privilege:
      try:
        privs_to_enable.append (int (priv), 0)
      except ValueError:
        privs_to_enable.append (Privilege.from_string (priv).luid, 0)
    win32security.AdjustTokenPrivileges (self.hToken, 0, privs_to_enable)
    self._dirty = True

class SID (_SecurityObject):

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
    return SID (ConvertStringSidToSid (string))

class Account (_SecurityObject):

  def __init__ (self, sid, system_name="", attributes=None):
    self.reset (sid, system_name="", attributes=None)
    
  def reset (self, sid, system_name, attributes):
    self.sid = SID (sid)
    self.attributes = attributes
    try:
      self.name, self.domain, self.type = win32security.LookupAccountSid (system_name, sid)
    except win32security.error, (errno, context, errmsg):
      self.name = self.domain = ""
      self.type = None
    self._update ()

  def __repr__ (self):
    return r"<Account: %s [%s]>" % (self, self.sid)

  def pyobject (self):
    return self.sid.pyobject ()
  
  def as_string (self):
    if self.domain:
      return r"%s\%s" % (self.domain, self.name)
    else:
      return self.name or str (self.sid)
  
  @staticmethod
  def from_name (account_name, system_name=""):
    sid, domain, type = win32security.LookupAccountName (system_name, account_name)
    return Account (sid, domain)
    
ACE_TYPES = Partial (symbol, pattern="%s_ACE_TYPE")
class ACE (_SecurityObject):

  TYPES = {
    win32security.ACCESS_ALLOWED_ACE_TYPE : "Access Allowed",
    win32security.ACCESS_DENIED_ACE_TYPE : "Access Denied",
    win32security.SYSTEM_AUDIT_ACE_TYPE : "System Audit",
    win32security.ACCESS_ALLOWED_OBJECT_ACE_TYPE : "Access Allowed",
    win32security.ACCESS_DENIED_OBJECT_ACE_TYPE : "Access Denied",
    win32security.SYSTEM_AUDIT_OBJECT_ACE_TYPE : "System Audit",
  }

  def __init__ (self, type, trustee, access, flags=set ()):
    """Construct a new ACE
    
    @param type String or number representing one of the *_ACE_TYPE constants
    @param trustee "domain\user" or Account instance representing the security principal
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
  
  def as_tuple (self):
    return self.type, self.account, self.mask
  
  def as_string (self):
    rights = mask_as_string (self.mask)
    return "%s %s %s" % (self.access, self.trustee, self.as_string (rights))
  
  def reset (self, type, trustee, access, flags):
    self.type = ACE_TYPES (type)
    (type, flags) = ace[0]
    if type in [win32security.ACCESS_ALLOWED_ACE_TYPE, win32security.ACCESS_DENIED_ACE_TYPE, win32security.SYSTEM_AUDIT_ACE_TYPE]:
      mask, sid = ace[1:]
    else:
      mask, object_type, inherited_object_type, sid = ace[1:]

    self.type = self.TYPES[type]
    self.mask = mask
    self.account = Account (sid)
    
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
    
  def __getitem__ (self, key):
    return self._ACE (self._acl.GetAce (key))

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

class Security (_SecurityObject):

  def __init__ (self, owner=None, group=None, dacl=None, sacl=None, inherit_handle=True):
    _SecurityObject.__init__ (self)
    self.reset (owner, group, dacl, sacl, inherit_handle)

  def __repr__ (self):
    self._update ()
    return win32security.ConvertSecurityDescriptorToStringSecurityDescriptor (
      self.pyobject ().SECURITY_DESCRIPTOR, 
      win32security.SDDL_REVISION_1,
      -1
    )
    
  def reset (self, owner, group, dacl, sacl, inherit_handle):
    self._sa = win32security.SECURITY_ATTRIBUTES ()
    self.inherit_handle = inherit_handle
    self.owner = self.group = self.dacl = self.sacl = None
    
    if owner:
      if isinstance (owner, Account):
        self.owner = owner
      else:
        self.owner = Account (owner)
      
    if group:
      if isinstance (group, Account):
        self.group = group
      else:
        self.group = Account (group)
        
    if dacl:
      if isinstance (dacl, DACL):
        self.dacl = dacl
      else:
        self.dacl = DACL (dacl)
    
    if sacl:
      if isinstance (sacl, SACL):
        self.sacl = sacl
      else:
        self.sacl = SACL (sacl)
        
    self._update ()
    
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
    
  @staticmethod
  def from_security_descriptor (sd, inherit_handle=True):
    """Factory method to construct a Security object from a PySECURITY_DESCRIPTOR 
    object.
    
    @param sd A PySECURITY_DESCRIPTOR instance
    @param inherit_handle A flag indicating whether the handle is to be inherited
    @return a Security instance
    """
    return Security (
      owner=sd.GetSecurityDescriptorOwner (),
      group=sd.GetSecurityDescriptorGroup (),
      dacl=sd.GetSecurityDescriptorDacl (),
      sacl=sd.GetSecurityDescriptorSacl (),
      inherit_handle=inherit_handle
    )
  
  @staticmethod
  def from_string (string):
    """Factory method to construct a Security object from a string in
    Microsoft SDDL format.
    
    @param string A string in Microsoft SDDL format
    @return A Security instance
    """
    return Security.from_security_descriptor (
      sd=win32security.ConvertStringSecurityDescriptorToSecurityDescriptor (
        string, 
        win32security.SDDL_REVISION_1
      )
    )
    
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
    @return a Security instance
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
      return Security.from_security_descriptor (sd=GetSecurityInfo (object, object_type, flags))
    else:
      return Security.from_security_descriptor (sd=GetNamedSecurityInfo (object, object_type, flags))

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
  adjust_privileges (SE_CHANGE_NOTIFY_NAME)
