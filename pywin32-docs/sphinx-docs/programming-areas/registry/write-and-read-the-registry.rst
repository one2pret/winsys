.. highlight:: python
   :linenothreshold: 5

===========================
Write and read the Registry
===========================

**The requirement**: To write keys and values of various types into the registry, 
including the default value for a key. Read them back afterwards.


The registry is organised into keys, subkeys and their values. A key
can have one default value (one without a name), any number of named
values, and any number of subkeys. Each subkey can itself have subkeys
and values. And so ad infinitum.

The type of each value must be specified from the list of those understood
by the registry. In practice most values will be strings (REG_SZ) or integers
(REG_DWORD). There are other possiblities, but anything else can always be
stuffed into a Blob and registered as binary (REG_BINARY).

The code below for writing uses CreateKey to ensure the key you're requesting
exists. If you're not specifying a value then that's all you get: just
the key. If you specify a named value, this is created: an empty string
for the name gives you a default value. The code assumes you want to store
the value as a string unless you specify otherwise.

The code for reading will fail if the keys or values requested are not
present.

-------
Writing
-------

.. literalinclude:: write_the_registry.py


.. note::

    * Rather than mess with the _winreg hive constants, you specify the
      hive (HKEY_LOCAL_MACHINE etc.) as the first part of the registry path
      string.

    * CreateKey will in fact return a key you can use, but you can't
      specify the access mode, so you won't be able to write back to
      it later. OpenKey allows you to specify access, but won't create the
      key if it's not there. Hence the two-handed approach.
      
    * A (unicode) string value is assumed to be the storage type, unless
      it's overridden by the datatype parameter.

    * The only way to get a non-integer number into the registry is to
      store its representation as a binary type. The struct module's pack
      function generate the right bytes for a floating-point numnber. Or
      you can use Python's pickle to serialize arbitrary objects.
  
-------
Reading
-------

.. literalinclude:: read_the_registry.py

----------
References
----------

.. seealso::

   `_winreg <http://docs.python.org/lib/module--winreg.html>`_
     The _winreg module at python.org
   `RegCreateKey <http://msdn.microsoft.com/en-us/library/ms724842(VS.85).aspx>`_
     The RegCreateKey function at microsoft.com
   `RegOpenKey <http://msdn.microsoft.com/en-us/library/ms724895(VS.85).aspx>`_
     The RegOpenKey function at microsoft.com
   `RegSetValueEx <http://msdn.microsoft.com/en-us/library/ms724923(VS.85).aspx>`_
     The RegSetValueEx function at microsoft.com
   `RegQueryValueEx <http://msdn.microsoft.com/en-us/library/ms724911(VS.85).aspx>`_
     The RegQueryValueEx function at microsoft.com
   `Registry Value Types <http://msdn.microsoft.com/en-us/library/ms724884(VS.85).aspx>`_
     The possible registry value types at microsoft.com