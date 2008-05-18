import _winreg

import walk_the_registry

OLD_VERSION = 1
NEW_VERSION = 2
OLD_PATH = r"c:\pysoftv%d" % OLD_VERSION
NEW_PATH = r"c:\pysoftv%d" % NEW_VERSION

regpath = r"HKEY_CURRENT_USER\Software\PySoft"
for (keyname, key), subkey_names, values in walk_the_registry.walk (regpath, True):
  for name, data, datatype in values:
    
    if datatype == _winreg.REG_SZ and OLD_PATH in data:
      _winreg.SetValueEx (key, name, None, datatype, data.replace (OLD_PATH, NEW_PATH))
      print "Replaced %s in %s" % (name, keyname)
    
    elif datatype == _winreg.REG_DWORD and data == 1:
      _winreg.SetValueEx (key, name, None, datatype, 2)
      print "Replaced %s in %s" % (name, keyname)