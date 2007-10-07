import os, sys
import glob
import re

#
# Find imports of the form:
#   import abcdef.idl
#
r_imports = re.compile (r'import "(\w+)\.idl"')

#
# Find interface definitions of the form:
# [
#   ...
#   uuid(abcd-efgh-...-xyz),
# ]
# interface IMyInterface : ISomeBaseInterface
# {
#   HRESULT DoSomething ([out] LPBLAH *blah);
# };
#
#
r_interface = re.compile (r"\[([^\]]*)\]\s+interface\s+(\w+)\s*:\s*(\w+)\s*{([^}]*})")

#
# Find parameter definitions of the form:
#   [in, out] LPBLAH *blah
#
r_param = re.compile (r"\[([^]]+)\]\s+(\w+)\s+(\**?\w+)")

#
# Find uuid of the form:
#   uuid(abcdef-gjj-...-xyz)
#
r_uuid = re.compile (r"uuid\(([^\)]*)\)")

#
# Find method definitions of the form:
#   HRESULT DoThing (...)
#
r_method = re.compile (r"\s*(\w+)\s+(\w+)\s*\(([^\)]+)\);")

#
# Find one-line aliases of the form:
#   typedef const STRUCT *LPSTRUCT;
#
r_aliases = re.compile (r"typedef\s+(?:const\s+)?(\w+)\s*(\**?\s*\w+)\s*;")

#
# Find struct definitions of the form:
#   struct XYZ
#   {
#      LONG abc;
#      DWORD *pxyz;
#   };
#
r_structs = re.compile (r"struct\s+(\w+)\s+{([^}]+)}")

#
# Find struct items of the form:
#   [pragmas] DWORD *pabc;
#
r_struct_items = re.compile (r"\s*(?:\[[^]]+\])?\s+(\w+)\s+(\**?\w+)\s*;")

def parse_idl (filename):
    
  def get_imports (text):
    return r_imports.findall (text)
    
  def get_aliases (text):
    return [(rhs.replace (" ", ""), lhs.replace (" ", "")) for (rhs, lhs) in r_aliases.findall (text)]
    
  def get_structures (text):
    def get_items (text):
      return r_struct_items.findall (text)
    
    structures = {}
    for name, params in r_structs.findall (text):
      structures[name] = get_items (params)
    return structures
          
  def get_interfaces (text):

    def get_uuid (text):
      uuid_match = r_uuid.search (text)
      if uuid_match:
        return uuid_match.group (1)
      else:
        return ""

    def get_method_defs (text):
      method_defs = {}
      for result, name, params in r_method.findall (methods):
        param_defs = r_param.findall (params)
        method_defs[name] = (result, param_defs)
      return method_defs
        
    interfaces = {}
    for info, interface, base, methods in r_interface.findall (text):
      uuid = get_uuid (info)
      method_defs = get_method_defs (methods)
      interfaces[interface] = uuid, base, method_defs
    return interfaces
    
  text = open (filename).read ()
  imports = get_imports (text)  
  aliases = get_aliases (text)
  structures = get_structures (text)
  interfaces = get_interfaces (text)
  return imports, aliases, structures, interfaces

param_xforms = {
  "POINTER (void)" : "c_void_p"
}

#
# Write the module out
#
def write_module (ofilename, imports, aliases, structures, interfaces):
  
  def write_imports (imports):
    for i in imports:
      imp = i.lower ()
      yield "from %(imp)s import *\n" % locals ()

  def write_aliases (aliases):
    for rhs, lhs in aliases:
      while lhs.startswith ("*"):
        rhs = "POINTER (%s)" % rhs
        lhs = lhs[1:]
      yield "%(lhs)s = %(rhs)s\n" % locals ()
      
  def write_interface (interface, uuid, base, method_defs):
    
    def write_method_defs (method_defs):
      
      def write_params (params):
        for pdirection, ptype, pname in params:
          directions = ", ".join (["'%s'" % d.strip () for d in pdirection.split (",") if d.strip () in ("in", "out")])
          while pname.startswith ("*"):
            ptype = "POINTER (%s)" % ptype
            pname = pname[1:]
          #~ for before, after in param_xforms.items ():
            #~ paramtype = paramtype.replace (before, after)
          yield '[%(directions)s], %(ptype)s, "%(pname)s"' % locals ()
          
      for name, (restype, params) in method_defs.items ():
        yield "COMMETHOD ("
        yield '  [], %(restype)s, "%(name)s",' % locals ()
        for param in write_params (params):
          yield '  %(param)s,' % locals ()
        yield ")"
    
    method_defs = "\n    ".join (write_method_defs (method_defs))
    yield """
##
## %(interface)s
##
IID_%(interface)s = "{%(uuid)s}"

class %(interface)s (%(base)s):
  _iid_ = GUID (IID_%(interface)s)
  _methods_ = [
    %(method_defs)s
  ]
  
""" % locals ()

  odirectory = os.path.join ("idls")
  if not os.path.isfile (os.path.join (odirectory, "__init__.py")):
    open (os.path.join (odirectory, "__init__.py"), "w").close ()
  ofile = open (os.path.join ("idls", ofilename), "w")
  try:
    ofile.write ("from comtypes import *\n")
    ofile.write ("from ctypes.wintypes import *\n")
    ofile.writelines (write_imports (imports))
    ofile.write ("\n")
    ofile.writelines (write_aliases (aliases))
    ofile.write ("\n")
    for interface, (uuid, base, method_defs) in interfaces.items ():
      ofile.writelines (write_interface (interface, uuid, base, method_defs))
  finally:
    ofile.close ()
  
def main (directory):
  print "Scanning", os.path.join (directory, "*.idl")
  for filepath in glob.glob (os.path.join (directory, "*.idl")):
    print filepath
    imports, aliases, structures, interfaces = parse_idl (filepath)
    base, ext = os.path.splitext (os.path.basename (filepath))
    write_module (base.lower () + ".py", imports, aliases, structures, interfaces)

if __name__ == '__main__':
  if len (sys.argv) > 1:
    directory = sys.argv[1]
  else:
    directory = "."
  if directory == 'sdk':
    directory = r"C:\sdk\include"
  main (directory)
