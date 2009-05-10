# -*- coding: iso-8859-1 -*-
import pywintypes

class x_winsys (pywintypes.error):
  u"""Base for all WinSys exception. Subclasses pywintypes.error so that
  except pywintypes.error clauses can be used to catch all relevant exceptions
  """
  def __init__ (self, errno, errctx, errmsg):
    #
    # Attempt to ensure that the correct sequence of arguments is
    # passed to the exception: this makes for more sane error-trapping
    # at the cost of a certain flexibility.
    #
    pass
    
class x_access_denied (x_winsys):
  u"General purpose access-denied exception"
  
class x_not_found (x_winsys):
  u"General purpose not-found exception"

class x_invalid_handle (x_winsys):
  u"General purpose invalid-handle exception"

def wrapper (winerror_map, default_exception=x_winsys):
  u"""Used by each module to map specific windows error codes onto
  Python exceptions. Always includes a default which is raised if
  no specific exception is found.
  """
  def _wrapped (function, *args, **kwargs):
    u"""Call a Windows API with parameters, and handle any
    exception raised either by mapping it to a module-specific
    one or by passing it back up the chain.
    """
    try:
      return function (*args, **kwargs)
    except pywintypes.error, (errno, errctx, errmsg):
      exception = winerror_map.get (errno, default_exception)
      raise exception (errno, errctx, errmsg)
    except (WindowsError, IOError), err:
      exception = winerror_map.get (err.errno, default_exception)
      if exception:
        raise exception (err.errno, "", err.strerror)
  return _wrapped
