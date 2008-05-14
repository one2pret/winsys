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
  detail and this function takes care of it by expecting a string and
  simply picking the right constant out of the _winreg implementation.

* To iterate over all the keys or value in a particular place in the
  registry, you can either use one of the Query functions up front and
  then loop over an exact count or, as we're doing here, simply iterate
  until you catch an EnvironmentError. This is slightly preferable as
  it should take account of changes to the keys while you're looping.

* The minimal RegKey class is helpful because it's not otherwise easy to get
  the name of a key from its handle.

* As it stands you can't modify through the keys returned from this
  function: for that you need to OR-in _winreg.KEY_SET_VALUE at line 30.