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

.. literalinclude:: walk_the_registry.py

-----
Notes
-----

* Most API-level functions require the use of constants to indicate
  one of the hives (the registry roots) but this is really an implementation
  detail and the walk function takes care of it by expecting a string and
  simply picking the right constant out of the _winreg implementation.

* To iterate over all the keys or value in a particular place in the
  registry, you can either use one of the RegQuery functions up front and
  then loop over an exact count or, as we're doing here, simply iterate
  until you catch an EnvironmentError. This is slightly preferable as
  it should take account of changes to the keys while you're looping.

-----------------------------------
Bonus: Writing back to the registry
-----------------------------------

By default, the code offers a read-only view of the registry. If you wanted
to update the values you're iterating over, you'd need to pass False as the
second parameter. This results in keys being opened with the _winreg.KEY_SET_VALUE 
flag allowing you to set their values later.

Here's an example which upgrades all pysoft software from v1 to v2. It assumes 
that the earlier walk function is available in module registry_walker.py.

.. literalinclude:: walk_the_registry_writer.py

----------
References
----------

.. seealso::

   `_winreg <http://docs.python.org/lib/module--winreg.html>`_
     The _winreg module at python.org
   `RegOpenKey <http://msdn.microsoft.com/en-us/library/ms724895(VS.85).aspx>`_
     The RegOpenKey function at microsoft.com
   `RegEnumKey <http://msdn.microsoft.com/en-us/library/ms724861(VS.85).aspx>`_
     The RegEnumKey function at microsoft.com
   `RegEnumValue <http://msdn.microsoft.com/en-us/library/ms724865(VS.85).aspx>`_
     The RegEnumValue function at microsoft.com
   `Registry Value Types <http://msdn.microsoft.com/en-us/library/ms724884(VS.85).aspx>`_
     The possible registry value types at microsoft.com
   `Registry Key Access Rights <http://msdn.microsoft.com/en-us/library/ms724878(VS.85).aspx>`_
     Registry key access and security flags at microsoft.com
  