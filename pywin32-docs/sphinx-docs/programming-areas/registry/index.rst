======================
Accessing the Registry
======================

The registry is a central point of storage for all manner of configuration
information on a Windows machine. It consists of three broad areas: system-level
information, user-level information and on-the-fly information. Areas of the
registry can be controlled using standard Windows security functionality and
the user section of the registry is copied about when roaming profiles are
enabled.

Access to the registry is traditionally controlled by a series of API calls,
most of which have the prefix Reg. Since Python 2.0, the stdlib has included
a _winreg module, which is, as the leading underscore and its documentation
suggests, a low-level module merely wrapping the API calls. The initial idea was
that a more Pythonic module would wrap this lower-level functionality. However, 
no higher-level module has been written for the stdlib and the reorg happening 
for Python 3.0 is set to rename it to winreg. Note that a number of helper
modules have been written by third parties, offering class or dictionary-style
access to the registry and these are available from PyPI, as recipes on the
Python Cookbook site or from individuals' websites.

At the same time, the pywin32 extensions offer a largely overlapping set of
functions in the win32api module, and it's also possible to access the registry
via WMI. Of course the ctypes module can give you the same access with a little
more work and since there are functions unwrapped by either pywin32 or by _winreg 
(RegCreateKeyEx for example) these can be accessed by ctypes.

Of course, a final -- if slightly desperate -- approach is to construct or adapt
a .reg text file as exported from regedit, and call regedit <filename>.reg to
import it. Crude, but a useful fallback.

