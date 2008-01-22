import os, sys
import _winreg

if __name__ == '__main__':
  release_dir = os.path.dirname (sys.executable)
  release_path = os.path.join (release_dir, "release.exe")
  if not os.path.isfile (release_path):
    raise RuntimeError, "Can't find %s" % release_path
    
  HKCR = _winreg.HKEY_CLASSES_ROOT
  _winreg.SetValue (
    HKCR,
    r".release",
    _winreg.REG_SZ,
    "release.specfile"
  )
  _winreg.SetValue (
    HKCR, 
    r"release.specfile\Shell\Release\Command", 
    _winreg.REG_SZ, 
    '%s "%%1" %%*' % release_path
  )
