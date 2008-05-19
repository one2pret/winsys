.. highlight:: python
   :linenothreshold: 5

========================
Delete from the Registry
========================

**The requirement:** To delete one or more keys from the registry, including 
all their values.

The standard registry API, exposed in Python by the _winreg module, only allows
keys to be deleted which have no subkeys. The Windows shell API
does offer a recursive key delete but that function isn't exposed neither by the
Python stdlib nor by the pywin32 extensions.

The first example below uses the _winreg module to delete keys one at a time.
For simplicity, this example knows the layout of subtrees it needs to delete.
It would be possible to adapt the registry walker example to go depth first
and delete subtrees from the bottom up. The second example uses ctypes to
invoke the shell API function which will delete an entire tree in one go.

---------------------
Deleting with _winreg
---------------------

.. literalinclude:: delete_the_registry_winreg.py

.. note::

    * DeleteKey only operates on an open key and a subkey name: you can't open
      the key to be deleted and then pass None for the subkey.
      
    * The key whose subkey is being deleted must have been opened with enough
      access to delete a subkey.

  
-----------------------
Deleting with Shell API
-----------------------

.. literalinclude:: delete_the_registry_shell.py

.. note::

    * As we're using the unicode variant of the SHDeleteKey function the
      string identifying the subkey to be removed must be a Python unicode
      string.

.. seealso::

   `RegDeleteKey <http://msdn.microsoft.com/en-us/library/ms724845(VS.85).aspx>`_
     Documentation on microsoft.com for RegDeleteKey, the function underlying _winreg.DeleteKey

   `SHDeleteKey <http://msdn.microsoft.com/en-us/library/bb773486(VS.85).aspx>`_
     Documentation on microsoft.com for SHDeleteKey
