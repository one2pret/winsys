import os, sys
import _winreg
import win32api
import win32security

#
# You need to have SeBackupPrivilege enabled for this to work
#
priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
hToken = win32security.OpenProcessToken (win32api.GetCurrentProcess (), priv_flags)
privilege_id = win32security.LookupPrivilegeValue (None, "SeBackupPrivilege")
win32security.AdjustTokenPrivileges (hToken, 0, [(privilege_id, win32security.SE_PRIVILEGE_ENABLED)])

root = _winreg.OpenKey (_winreg.HKEY_CURRENT_USER, r"Software\PySoft")
filepath = "PySoft.registry"
if os.path.exists (filepath):
  os.unlink (filepath)
_winreg.SaveKey (root, filepath)
print "Saved PySoft as", filepath
