#include <python.h>
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <sddl.h>

#ifndef F_OK
#define F_OK 0
#endif
#ifndef R_OK
#define R_OK 4
#endif
#ifndef W_OK
#define W_OK 2
#endif
#ifndef X_OK
#define X_OK 1
#endif

static PyObject*
winaccess (PyObject *self, PyObject *args)
{
    SECURITY_INFORMATION requested_information = OWNER_SECURITY_INFORMATION | GROUP_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION;
    PSECURITY_DESCRIPTOR pSD = NULL;
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
    long mode;
	
    if (!PyArg_ParseTuple (args, "Oi:winaccess", &filepath, &mode)) {
        PyErr_SetString (PyExc_TypeError, "PROBLEM");
        return NULL;
    }
    
    if (PyUnicode_Check (filepath)) {
        GetFileSecurityW (PyUnicode_AS_UNICODE (filepath),
            requested_information, 0, 0, &dwSize);
        pSD = (PSECURITY_DESCRIPTOR)malloc(dwSize);
        if (!GetFileSecurityW (PyUnicode_AS_UNICODE (filepath),
            requested_information, pSD, dwSize, &dwSize)) {
            sprintf (exception_string, "FileSecurity: %d\n", GetLastError ());
            PyErr_SetString (PyExc_RuntimeError, exception_string);
            goto finish;
        }
    }
    /*
    else {
        GetFileSecurityA (PyString_AS_STRING (filepath),
            requested_information, 0, 0, &dwSize);
        security_descriptor = (PSECURITY_DESCRIPTOR)malloc(dwSize);
        if (!GetFileSecurityA (PyString_AS_STRING (filepath),
            requested_information, security_descriptor, dwSize, &dwSize)) {
            sprintf (exception_string, "FileSecurity: %d\n", GetLastError ());
            PyErr_SetString (PyExc_RuntimeError, exception_string);
            goto finish;
        }
    }
    */
    
    if (!IsValidSecurityDescriptor (pSD)) {
        PyErr_SetString (PyExc_OSError, "Security Descriptor is invalid");
        goto finish;
    }
    
    if (!ImpersonateSelf (SecurityImpersonation)) {
        PyErr_SetString (PyExc_OSError, "Unable to impersonate self");
        goto finish;
    }
    
    if (!OpenThreadToken (GetCurrentThread (), TOKEN_ALL_ACCESS, 
        TRUE, &hToken)) {
        PyErr_SetString (PyExc_OSError, "Unable to open thread token");
        goto finish;
    }

    mapping.GenericRead = FILE_READ_DATA; 
    mapping.GenericWrite = FILE_WRITE_DATA;
    mapping.GenericExecute = FILE_EXECUTE;
    mapping.GenericAll = FILE_ALL_ACCESS;
    
    access_desired = 0;
    if (mode & X_OK)
      access_desired |= FILE_EXECUTE;
    if (mode & R_OK)
      access_desired |= FILE_READ_DATA;
    if (mode & W_OK)
      access_desired |= FILE_WRITE_DATA;
    MapGenericMask (&access_desired, &mapping);
	   
    if (!AccessCheck (
        pSD, hToken, access_desired, &mapping, &privilege_set,
        &privilege_set_size, &access_granted, &is_access_granted)) {

        sprintf (exception_string, "AccessCheck: %d\n", GetLastError ());
        PyErr_SetString (PyExc_RuntimeError, exception_string);
        goto finish;
    }
    
finish:
    RevertToSelf ();
    if (pSD)
        free (pSD);
    if (hToken != INVALID_HANDLE_VALUE)
        CloseHandle (hToken);
    
    if (PyErr_Occurred())
        return NULL;
    else
        return PyBool_FromLong (is_access_granted);
}

static PyMethodDef extension_methods[] = {
  {"winaccess", winaccess, METH_VARARGS, "Get windows file security"},
  {NULL, NULL}
};

PyMODINIT_FUNC
initextension (void)
{
  Py_InitModule3("extension", extension_methods, "Extension docstring");
}