.. Python on Windows master file, created by sphinx-quickstart on Sun May 11 19:51:25 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python on Windows
=================

Using Python under Windows is straightforward and powerful, thanks
to the hard work put in over the years by the core Python development
and documentation teams and especially to the developers of the 
`pywin32 extensions <http://pywin32.sf.net>`_. However, those
extensions consist mostly of python wrappers around the Win32
API with some higher level modules and classes on top. And
the extensive .chm documentation which comes with the packages
reflects that fact, outlining functions and modules mostly in
terms of their corresponding API.

This in turn means that people with more experience answer the
same questions again and again on the Python mailing lists. This
community-produced documentation set hopes to present a more readable
and solution-oriented basis for helping Python developers to make
use of the really quite extensive capabilities available to them
under Windows.

Although we have highlighted the pywin32 extensions, there are
many other Windows-specific modules available, both within Python's
stdlib itself and produced by third-party developers and available
via PyPI or from individual's sites. These may in turn be based on
the pywin32 modules or on the `comtypes <http://ctypes.sf.net>`_ 
extension to ctypes or may be built from scratch.

Contents:

.. toctree::
   :maxdepth: 2
   
   getting-started
   programming-areas/index
   resources

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

