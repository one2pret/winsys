import sys, os
import pythoncom
import winerror
from win32com.shell import shell, shellcon
from win32com.server.util import wrap, NewEnum
from win32com.server.exception import COMException

IPersist_Methods = ["GetClassID"]
IPersistFolder_Methods = IPersist_Methods + ["Initialize"]
IShellFolder_Methods = [
  "CreateViewObject",
  "EnumObjects",
  "ParseDisplayName",
  "BindToObject",
  "BindToStorage",
  "CompareIDs", 
  "GetUIObjectOf",
  "GetDisplayNameOf",
  "GetAttributesOf",
  "SetNameOf",
]

class ShellFolderRoot:
  _reg_progid_ = "TJG.NamespaceExtension.Step1"
  _reg_desc_ = "TJG Namespace Extension - Step1"
  _reg_clsid_ = "{398ADD84-73CB-4d63-BA91-F42D9D986A3E}"

  _com_interfaces_ = [
    pythoncom.IID_IPersist,
    shell.IID_IPersistFolder,
    shell.IID_IShellFolder,
  ]
  _public_methods_ = IPersistFolder_Methods + IShellFolder_Methods

  def GetClassID(self):
    return self._reg_clsid_
  
  def Initialize(self, pidl):
    self.pidl = pidl
  
  def CreateViewObject(self, hwnd, iid):
    raise COMException (hresult=winerror.E_NOTIMPL)
  
  def EnumObjects(self, hwndOwner, flags):
    return NewEnum ([], iid=shell.IID_IEnumIDList)
  
  def ParseDisplayName (self, hwnd, reserved, displayName, attr):
    raise COMException (hresult=winerror.E_NOTIMPL)
  
  def BindToStorage(self, pidl, bc, iid):
    raise COMException (hresult=winerror.E_NOTIMPL)
  
  def BindToObject(self, pidl, bc, iid):
    raise COMException (hresult=winerror.E_NOTIMPL)

  def CompareIDs(self, param, id1, id2):
    return cmp (id1, id2)
  
  def GetUIObjectOf(self, hwndOwner, pidls, iid, inout):
    raise COMException (hresult=winerror.E_NOTIMPL)

  def GetDisplayNameOf(self, pidl, flags):
    raise COMException (hresult=winerror.E_NOTIMPL)
  
  def GetAttributesOf(self, pidls, attrFlags):
    raise COMException (hresult=winerror.E_NOTIMPL)

def DllRegisterServer():
  import _winreg
  key = _winreg.CreateKey (
    _winreg.HKEY_LOCAL_MACHINE,
    "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\" \
      "Explorer\\Desktop\\Namespace\\" + \
      ShellFolderRoot._reg_clsid_
  )
  _winreg.SetValueEx (key, None, 0, _winreg.REG_SZ, ShellFolderRoot._reg_desc_)
  # And special shell keys under our CLSID
  key = _winreg.CreateKey (
    _winreg.HKEY_CLASSES_ROOT,
    "CLSID\\" + ShellFolderRoot._reg_clsid_ + "\\ShellFolder"
  )
  # 'Attributes' is an int stored as a binary! use struct
  attr = shellcon.SFGAO_FOLDER | shellcon.SFGAO_HASSUBFOLDER | shellcon.SFGAO_BROWSABLE
  import struct
  s = struct.pack ("i", attr)
  _winreg.SetValueEx (key, "Attributes", 0, _winreg.REG_BINARY, s)
  print ShellFolderRoot._reg_desc_, "registration complete."

def DllUnregisterServer():
  import _winreg
  try:
    key = _winreg.DeleteKey (
      _winreg.HKEY_LOCAL_MACHINE,
      "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\" \
        "Explorer\\Desktop\\Namespace\\" + \
        ShellFolderRoot._reg_clsid_
    )
  except WindowsError, details:
    import errno
    if details.errno != errno.ENOENT:
      raise
  print ShellFolderRoot._reg_desc_, "unregistration complete."

if __name__=='__main__':
  from win32com.server import register
  register.UseCommandLine (
    ShellFolderRoot,
    finalize_register = DllRegisterServer,
    finalize_unregister = DllUnregisterServer
  )
