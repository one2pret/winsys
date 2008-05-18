import _winreg
import ctypes

shlwapi = ctypes.windll.shlwapi
SHDeleteKey = shlwapi.SHDeleteKeyW
HKCU = ctypes.wintypes.HKEY (_winreg.HKEY_CURRENT_USER)

SHDeleteKey (HKCU, ur"Software\PySoft")
