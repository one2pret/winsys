class K (object):
  
  def __init__ (self, s, n):
    self.string = s
    self.number = n
    
  def __repr__ (self):
    return self.number
  
  def __str__ (self):
    return self.string


class Constants (object):

  def __init__ (self):
    pass
  
  def from_dict (self, name, mapping, pattern="*"):
    constants = self.get (name, {})
    for k, v in mapping.items ():
      constants[str (k).lower ()] = v
    self[name] = self.Constant (constants, pattern)
    return self[name]

  def from_namespace (self, name, pattern="*", namespace=win32security):
    return self.from_list (name, fnmatch.filter (dir (namespace), pattern), pattern, namespace)
    
  def from_list (self, name, keys, pattern="*", namespace=win32security):
    return self.from_dict (name, dict ((key, getattr (namespace, key)) for key in keys), pattern)

constants = Constants ()
ACE_FLAGS = constants.from_list ("ace_flags", ["CONTAINER_INHERIT_ACE", "INHERIT_ONLY_ACE", "INHERITED_ACE", "NO_PROPAGATE_INHERIT_ACE", "OBJECT_INHERIT_ACE"])
ACE_TYPES = constants.from_namespace ("ace_types", "*_ACE_TYPE")
DACE_TYPES = constants.from_namespace ("dace_types", "ACCESS_*_ACE_TYPE")
SACE_TYPES = constants.from_namespace ("sace_types", "SYSTEM_*_ACE_TYPE")
PRIVILEGE_ATTRIBUTES = constants.from_namespace ("privilege_attributes", "SE_PRIVILEGE_*")
PRIVILEGES = constants.from_namespace ("privileges", "SE_*_NAME")


print 