.. highlight:: python
   :linenothreshold: 5

=================
Walk the Registry
=================

---------------
The requirement
---------------

To walk down the registry in the style of the
os.walk function, yielding the current location, keys and values.

--------
The code
--------

.. literalinclude:: walk-the-registry.py

-----
Notes
-----

* Most API-level functions require the use of constants to indicate
  one of the hives (the registry roots) but this is really an implementation
  detail and the walk function takes care of it by expecting a string and
  simply picking the right constant out of the _winreg implementation.

* To iterate over all the keys or value in a particular place in the
  registry, you can either use one of the Query functions up front and
  then loop over an exact count or, as we're doing here, simply iterate
  until you catch an EnvironmentError. This is slightly preferable as
  it should take account of changes to the keys while you're looping.

* The minimal RegKey class is helpful because it's not otherwise easy to get
  the name of a key from its handle.

-----------------------------------
Bonus: Writing back to the registry
-----------------------------------

As it stands, this code offers a read-only view of the registry. If you wanted
to update the values you're iterating over, you'd need to bitwise-or the
_winreg.KEY_SET_VALUE constant into the OpenKey function at line 29.

Here's an example which assumes that you've relocated your Python interpreter
but that the registry settings haven't caught up. It assumes that the earlier
walk function is available and that you've modified to allow values to be
updated::

  import _winreg
  
  OLD_PATH = r"c:\python25"
  NEW_PATH = r"c:\python252"
  
  regpath = r"HKEY_LOCAL_MACHINE\Software\Python\PythonCore\2.5"
  for key, subkey_names, values in walk (regpath):
    for name, data, datatype in values:
      if datatype == _winreg.REG_SZ and OLD_PATH in data:
        _winreg.SetValueEx (key.key, name, None, datatype, data.replace (OLD_PATH, NEW_PATH)
        print "Replaced %s in %s" % (name, key)