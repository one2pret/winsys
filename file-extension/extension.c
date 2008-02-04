#include <python.h>
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

static PyObject*
extension_attribs(PyObject *self, PyObject *args)
{
  LPCTSTR lpFileName;
  DWORD result;
  
  if (!PyArg_ParseTuple (args, "s", &lpFileName)) {
    return NULL;
  }
  
  if ((result = GetFileAttributes (lpFileName)) == INVALID_FILE_ATTRIBUTES) {
    PyErr_SetString (PyExc_RuntimeError, "No such file");
    return NULL;
  }
  if (result & FILE_ATTRIBUTE_READONLY) {
    return Py_BuildValue ("s", "READONLY");
  }
  else
  {
    return Py_BuildValue ("s", "NOT-READONLY");
  }
}

static PyObject*
windows_file_security (PyObject *self, PyObject *args)
{
	SECURITY_INFORMATION requested_information = DACL_SECURITY_INFORMATION;
	PSECURITY_DESCRIPTOR security_descriptor = NULL;
	DWORD dwSize = 0;
	//~ HANDLE hToken;
	//~ DWORD access_desired;

	//~ GENERIC_MAPPING mapping;
	//~ mapping.GenericRead = 0; 
	//~ mapping.GenericWrite = GENERIC_WRITE;
	//~ mapping.GenericExecute = 0;
	//~ mapping.GenericAll = 0;
  //~ PRIVILEGE_SET privilege_set;
  
  PyObject *ofilepath;
  LPCWSTR *filepath;
	
  if (!PyArg_UnpackTuple (args, "windows_file_security", 1, 1, &filepath)) {
    return NULL;
  }
  
  if (!filepath = PyString_AsString (ofilepath)) {
    return NULL
  }
  
  if (GetFileSecurityW (filepath, requested_information, security_descriptor, dwSize, &dwSize)) {
    PyErr_SetString (PyExc_RuntimeError, "Problem getting security");
		return NULL;
  }
	//~ security_descriptor = (PSECURITY_DESCRIPTOR)malloc(dwSize);
	//~ if (security_descriptor == NULL)
		//~ return -2;
	//~ if (!GetFileSecurityW (PyUnicode_AS_UNICODE (filepath), requested_information, security_descriptor, dwSize, &dwSize))
		//~ return -3;
	//~ if (!ImpersonateSelf (SecurityImpersonation))
		//~ return -4;
	//~ if (!OpenThreadToken (GetCurrentThread (), TOKEN_ALL_ACCESS, TRUE, &hToken))
		//~ return -5;
	//~ MapGenericMask (&access_desired, &mapping);

	//~ RevertToSelf ();
	//~ free (security_descriptor);
	//~ return 1;
  
  Py_INCREF (filepath);
  return filepath;
}



static PyMethodDef extension_methods[] = {
  {"attribs", extension_attribs, METH_VARARGS, "Get attributes for a file"},
  {"windows_file_security", windows_file_security, METH_VARARGS, "Get windows file security"},
  {NULL, NULL}
};

PyMODINIT_FUNC
initextension (void)
{
  Py_InitModule3("extension", extension_methods, "Extension docstring");
}