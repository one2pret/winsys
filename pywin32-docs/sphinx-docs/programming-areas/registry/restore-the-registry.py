import os, sys
import ctypes
from ctypes import wintypes
import _winreg
import win32api
import win32security

#
# You need to have SeBackupPrivilege enabled for this to work
#
priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
hToken = win32security.OpenProcessToken (win32api.GetCurrentProcess (), priv_flags)
backup_privilege_id = win32security.LookupPrivilegeValue (None, "SeBackupPrivilege")
restore_privilege_id = win32security.LookupPrivilegeValue (None, "SeRestorePrivilege")
win32security.AdjustTokenPrivileges (
  hToken, 0, 
  [
    (backup_privilege_id, win32security.SE_PRIVILEGE_ENABLED),
    (restore_privilege_id, win32security.SE_PRIVILEGE_ENABLED)
  ]
)

advapi = ctypes.windll.Advapi32
RegRestoreKey = advapi.RegRestoreKeyW
_winreg.CreateKey (_winreg.HKEY_CURRENT_USER, ur"Software\PySoft2")
hKey = wintypes.HKEY (int (_winreg.OpenKey (_winreg.HKEY_CURRENT_USER, r"Software", 0, _winreg.KEY_WRITE)))
filepath = u"PySoft.registry"
print RegRestoreKey (hKey,  filepath, 0)
print "Restored PySoft to PySoft2"
