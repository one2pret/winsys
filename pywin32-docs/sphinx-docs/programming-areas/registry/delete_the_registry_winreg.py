import _winreg

def delete_key (top):
  if "\\" not in top: top += "\\"
  root, subkey = top.split ("\\", 1)
  if not subkey:
    raise RuntimeError, "Can't delete a registry hive"
  subkey_parts = subkey.split ("\\")
  subkey, tail = "\\".join (subkey_parts[:-1]), subkey_parts[-1]
  
  key = _winreg.OpenKey (getattr (_winreg, root), subkey, 0, _winreg.KEY_ALL_ACCESS)
  _winreg.DeleteKey (key, tail)


if __name__ == '__main__':
  delete_key (r"HKEY_CURRENT_USER\Software\PySoft\PyApp")
  delete_key (r"HKEY_CURRENT_USER\Software\PySoft\PyTool")
  delete_key (r"HKEY_CURRENT_USER\Software\PySoft\PyThing")
  delete_key (r"HKEY_CURRENT_USER\Software\PySoft")
