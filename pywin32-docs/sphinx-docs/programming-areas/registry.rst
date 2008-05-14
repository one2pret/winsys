======================
Accessing the Registry
======================

------------
Introduction
------------

The registry is a central point of storage for all manner of configuration
information on a Windows machine. It consists of three broad areas: system-level
information, user-level information and on-the-fly information. Areas of the
registry can be controlled using standard Windows security functionality and
the user section of the registry is copied about when roaming profiles are
enabled. It's possible (and sometimes desirable) to connect to the
registry on a remote computer.

Access to the registry is possible under Python by a number of different
routes. A non-exhaustive list includes: WMI, the _winreg module in the
stdlib, the Reg... functions in the pywin32 modules, and the ctypes
module. (You could also get fancy with various command line tools and
the Windows Scripting Host &c.)

---------------
Initial Example
---------------

This first simple example of registry access is presented using
four different approaches to illustrate the differences between
them. Further examples will mostly use the stdlib _winreg module
unless the job requires something else.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Read the user-specific PATH from the registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user-specific environment variables (from the [Advanced] tab of
the System Properties dialog box) are held in HKCU\\Environment which
is a dynamic copy of HKU\\<user SID>\\Environment. These values are
merged with the system values to form a the working environment for
a process. For this example, we want to read the PATH value from
the current user's environment settings. The full registry path to
this is: HKEY_CURRENT_USER\\Environment\\PATH.

**Using stdlib**::

  import _winreg

  hKey = _winreg.OpenKey (_winreg.HKEY_CURRENT_USER, r"Environment")
  value, type = _winreg.QueryValueEx (hKey, "PATH")

  print value
  

**Using pywin32**::

  import win32api
  import win32con
  
  hKey = win32api.RegOpenKey (win32con.HKEY_CURRENT_USER, r"Environment")
  value, type = win32api.RegQueryValueEx (hKey, "PATH")
  
  print value


**Using WMI**::

  import win32com.client
  
  HKEY_CURRENT_USER = 0x80000001L
  reg = win32com.client.GetObject ("winmgmts://./root/default:StdRegProv")
  
  in_parameters = reg.Methods_ ("GetStringValue").InParameters
  in_parameters.Properties_ ("hDefKey").Value = HKEY_CURRENT_USER
  in_parameters.Properties_ ("sSubKeyName").Value = r"Environment"
  in_parameters.Properties_ ("sValueName").Value = r"PATH"
  result = reg.ExecMethod_ ("GetStringValue", in_parameters)
  
  print result.Properties_ ("sValue").Value


**Using ctypes**::

  from ctypes import windll, create_string_buffer, byref
  from ctypes.wintypes import HKEY, DWORD
  advapi32 = windll.Advapi32
  
  HKEY_CURRENT_USER = 0x80000001L
  
  hKey = HKEY ()
  Type = DWORD ()
  buffer_size = 2048
  cbData = DWORD (buffer_size)
  Data = create_string_buffer (buffer_size)
  advapi32.RegOpenKeyW (HKEY_CURRENT_USER, u"Environment", byref (hKey))
  advapi32.RegQueryValueExW (hKey, u"PATH", None, byref (Type), Data, byref (cbData))
  
  print Data.raw[:cbData.value].decode ("utf16")[:-1]


.. note::

   For the purposes of clarity, I've taken several shortcuts in this ctypes
   example. I'm not checking the return values from the RegW functions,
   nor am I doing the "how-much-buffer-space-do-I-need?" dance with the
   cbData parameter
   
This particular example is almost as simple as it gets and the brevity
of all the solutions reflects this. Naturally, the ctypes solution
requires more explicit plumbing than the others where the plumbing is
mostly hidden behind library panelling.

The stdlib and pywin32 solutions are almost identical as is to be
expected since the stdlib module is pretty much a port of the
equivalent functions from the pywin32 win32api module by its author.
WMI offers slightly higher level functionality, but its own plumbing
gets in the way of a clear solution. ctypes, naturally, combines
complete flexibility with the need to get the plumbing exactly right.

-------------
More Examples
-------------

.. toctree::

   registry/walk-the-registry