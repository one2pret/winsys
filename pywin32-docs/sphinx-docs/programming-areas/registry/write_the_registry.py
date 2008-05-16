import _winreg

def write_value (keypath, value_name=None, value=None, datatype=None):
  keymode = _winreg.KEY_READ | _winreg.KEY_SET_VALUE
  if "\\" not in keypath: keypath += "\\"
  root, subkey = keypath.split ("\\", 1)
  _winreg.CreateKey (getattr (_winreg, root), subkey)
  
  if value_name is None:
    return
  
  key = _winreg.OpenKey (getattr (_winreg, root), subkey, 0, keymode)
  if datatype is None:
    if isinstance (value, type ("")):
      datatype = _winreg.REG_SZ
    elif isinstance (value, type (0)):
      datatype = _winreg.REG_DWORD
    else:
      raise RuntimeError, "Can't guess datatype for %s" % value
  
  _winreg.SetValueEx (key, value_name, 0, datatype, value)

if __name__ == '__main__':
  import struct
  
  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyThing"
  write_value (key_name)
  
  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyApp"
  write_value (key_name, "owner", "pysoft.co.uk")
  write_value (key_name, "version", struct.pack ("f", 1.2), _winreg.REG_BINARY)

  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyTool"
  write_value (key_name, "", "Tool for doing things with Python")
