#include <python.h>
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

static PyObject *
share_delete(PyObject *self, PyObject *args)
{
  PyUnicodeObject *filename;
  if (PyArg_ParseTuple (args, "U:share_delete", &filename)) {
    PyErr_SetString (PyExc_RuntimeError, "Couldn't read params");
    return NULL;    
  }
  
  return Py_BuildValue ("U", filename);
}

static PyMethodDef extension_methods[] = {
  {"share_delete", share_delete, METH_VARARGS, "Hold a file for share delete"},
  {NULL, NULL}
};

PyMODINIT_FUNC
initextension (void)
{
  Py_InitModule3("extension", extension_methods, "Extension docstring");
}