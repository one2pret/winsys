#include <python.h>
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

static PyObject*
windows_file_security (PyObject *self, PyObject *args)
{
    SECURITY_INFORMATION requested_information = DACL_SECURITY_INFORMATION |
        OWNER_SECURITY_INFORMATION | GROUP_SECURITY_INFORMATION;
    PSECURITY_DESCRIPTOR security_descriptor = NULL;
    DWORD dwSize = 0;
    char exception_string[256];
    HANDLE hToken = INVALID_HANDLE_VALUE;
    DWORD access_desired = 0;

    GENERIC_MAPPING mapping;
    PRIVILEGE_SET privilege_set;
    DWORD privilege_set_size = sizeof (privilege_set);
    DWORD access_granted = 0;
    BOOL is_access_granted = FALSE;
  
    PyObject *filepath;
	
    if (!PyArg_UnpackTuple (args, "windows_file_security", 1, 1, &filepath)) {
        goto finish;
    }
  
    if (!PyUnicode_Check (filepath) && !PyString_Check (filepath)) {
        PyErr_SetString (PyExc_RuntimeError, "File must be string or unicode");
        goto finish;
    }
    
    if (PyUnicode_Check (filepath)) {
        GetFileSecurityW (PyUnicode_AS_UNICODE (filepath),
            requested_information, 0, 0, &dwSize);
        security_descriptor = (PSECURITY_DESCRIPTOR)malloc(dwSize);
        if (!GetFileSecurityW (PyUnicode_AS_UNICODE (filepath),
            requested_information, security_descriptor, dwSize, &dwSize)) {
            sprintf (exception_string, "FileSecurity: %d\n", GetLastError ());
            PyErr_SetString (PyExc_RuntimeError, exception_string);
            goto finish;
        }
    }
    else {
        PyErr_SetString (PyExc_RuntimeError, "Only working with unicode");
        goto finish;
    }
    
    if (!ImpersonateSelf (SecurityImpersonation)) {
        PyErr_SetString (PyExc_RuntimeError, "Unable to impersonate self");
        goto finish;
    }
    
    if (!OpenThreadToken (GetCurrentThread (), TOKEN_ALL_ACCESS, 
        TRUE, &hToken)) {
        PyErr_SetString (PyExc_RuntimeError, "Unable to open thread token");
        goto finish;
    }

    mapping.GenericRead = FILE_GENERIC_READ; 
    mapping.GenericWrite = FILE_GENERIC_WRITE;
    mapping.GenericExecute = FILE_GENERIC_EXECUTE;
    mapping.GenericAll = FILE_ALL_ACCESS;
	  MapGenericMask (&access_desired, &mapping);
    
    if (!AccessCheck (
        security_descriptor, hToken, access_desired, &mapping, &privilege_set,
        &privilege_set_size, &access_granted, &is_access_granted)) {
        
        sprintf (exception_string, "AccessCheck: %d\n", GetLastError ());
        PyErr_SetString (PyExc_RuntimeError, exception_string);
        goto finish;
    }
    
finish:
    RevertToSelf ();
    if (security_descriptor) {
      free (security_descriptor);
    }
    if (hToken != INVALID_HANDLE_VALUE) {
        CloseHandle (hToken);
    }

    if (PyErr_Occurred()) {
        return NULL;
    } else {
        return Py_BuildValue ("i", is_access_granted);
    }
}

static PyMethodDef extension_methods[] = {
  {"windows_file_security", windows_file_security, METH_VARARGS, "Get windows file security"},
  {NULL, NULL}
};

PyMODINIT_FUNC
initextension (void)
{
  Py_InitModule3("extension", extension_methods, "Extension docstring");
}