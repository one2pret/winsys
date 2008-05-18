import _winreg

def write_value (keypath, value_name=None, value=None, datatype=_winreg.REG_SZ):
  keymode = _winreg.KEY_READ | _winreg.KEY_SET_VALUE
  if "\\" not in keypath: keypath += "\\"
  root, subkey = keypath.split ("\\", 1)
  _winreg.CreateKey (getattr (_winreg, root), subkey)
  
  if value_name is None:
    return
  
  key = _winreg.OpenKey (getattr (_winreg, root), subkey, 0, keymode)
  if datatype == _winreg.REG_SZ:
    value = unicode (value)  
  _winreg.SetValueEx (key, value_name, 0, datatype, value)



if __name__ == '__main__':
  import struct
  import pickle
  
  #
  # Just create the key
  #
  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyThing"
  write_value (key_name)
  
  #
  # Create the key if needed and write various data items
  #
  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyApp"
  write_value (key_name, "owner", u"Se\u00f1or Pit\u00f3n")
  write_value (key_name, "settings", ["abc", "def"], _winreg.REG_MULTI_SZ)
  write_value (key_name, "version", struct.pack ("f", 1.2), _winreg.REG_BINARY)
  write_value (key_name, "dump", pickle.dumps (object ()), _winreg.REG_BINARY)

  #
  # Create the key and populate the default value, assuming
  # conversion to string
  #
  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyTool"
  write_value (key_name, "", 1.1)
