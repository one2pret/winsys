import os, sys
import shutil
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

  scripter_path = os.path.join (os.environ['ProgramFiles'], "scripter")
  try:
    os.mkdir (scripter_path)
  except WindowsError, error:
    if not error.startswith ("[Error 183]"):
      raise
  
  shutil.copy (os.path.join (release_dir, "scripter.exe"), scripter_path)
