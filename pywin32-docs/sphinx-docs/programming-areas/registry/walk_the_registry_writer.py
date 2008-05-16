import _winreg

import registry_walker

OLD_PATH = r"c:\pysoftv1"
NEW_PATH = r"c:\pysoftv2"

regpath = r"HKEY_CURRENT_USER\Software\PySoft"
for (keyname, key), subkey_names, values in registry_walker.walk (regpath, True):
  for name, data, datatype in values:
    if datatype == _winreg.REG_SZ and OLD_PATH in data:
      _winreg.SetValueEx (key, name, None, datatype, data.replace (OLD_PATH, NEW_PATH))
      print "Replaced %s in %s" % (name, keyname)
