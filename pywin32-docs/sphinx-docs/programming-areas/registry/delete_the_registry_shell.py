import _winreg
import ctypes
from ctypes import wintypes

shlwapi = ctypes.windll.shlwapi
SHDeleteKey = shlwapi.SHDeleteKeyW
HKCU = wintypes.HKEY (_winreg.HKEY_CURRENT_USER)

SHDeleteKey (HKCU, ur"Software\PySoft")
