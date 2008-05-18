import _winreg

def read_value (keypath, value_name):
  keymode = _winreg.KEY_READ
  if "\\" not in keypath: keypath += "\\"
  root, subkey = keypath.split ("\\", 1)
  
  key = _winreg.OpenKey (getattr (_winreg, root), subkey, 0, keymode)
  return _winreg.QueryValueEx (key, value_name)


if __name__ == '__main__':
  import struct
  import pickle
  
  keypath = r"HKEY_CURRENT_USER\Software\PySoft\PyApp"
  value, datatype = read_value (keypath, "owner")
  print value
  value, datatype = read_value (keypath, "settings")
  print value
  value, datatype = read_value (keypath, "version")
  print struct.unpack ("f", value)[0]
  value, datatype = read_value (keypath, "dump")
  print pickle.loads (value)
  
  #
  # Read the default value
  #
  key_name = r"HKEY_CURRENT_USER\Software\PySoft\PyTool"
  value, datatype = read_value (key_name, "")
  print value
