from winsys import fs
import os
import filecmp
import shutil
import tempfile
import uuid
import win32file

#
# Convenience functions
#
def touch (filepath):
  open (os.path.join (TEST_ROOT, filepath), "w").close ()
  
def mkdir (filepath):
  os.mkdir (os.path.join (TEST_ROOT, filepath))
  
def rmdirs (filepath):
  shutil.rmtree (os.path.join (TEST_ROOT, filepath))
  
def dirs_are_equal (dir1, dir2):
  #
  # Make sure of same directory depth
  #
  if len (list (os.walk (dir1))) != len (list (os.walk (dir2))): 
    return False
  #
  # Make sure of directory contents
  #
  for (path1, dirs1, files1), (path2, dirs2, files2) in zip (
    os.walk (dir1), os.walk (dir2)
  ):
    if set (dirs1) != set (dirs2): 
      return False
    if set (files1) != set (files2):
      return False
    if any (not files_are_equal (os.path.join (path1, f1), os.path.join (path2, f2)) for f1, f2 in zip (files1, files2)):
      return False
  else:
    return True
    
def files_are_equal (f1, f2):
  if win32file.GetFileAttributesW (f1) != win32file.GetFileAttributesW (f2):
    return False
  if not filecmp.cmp (f1, f2, False):
    return False
  return True

def setup ():
  global TEST_ROOT
  TEST_ROOT = tempfile.mkdtemp ()
  print TEST_ROOT
  mkdir ("a")
  touch ("a/a.txt")
  mkdir ("a/b")
  touch ("a/b/b.txt")
  mkdir ("a/b/c")
  touch ("a/b/c/c.txt")
  
def teardown ():
  rmdirs (TEST_ROOT)

def test_FileAttributes():
  TempFile=os.path.expandvars("%temp%\\FileAtr.txt")
  try:
    open(TempFile,"w").close()
    assert win32file.GetFileAttributesW(TempFile)==fs.entry(TempFile).attributes.flags
  finally:
    os.unlink(TempFile)

def test_FileTempAttributes():
  TempFile=tempfile.NamedTemporaryFile()
  assert win32file.GetFileAttributesW(TempFile.name)==fs.entry(TempFile.name).attributes.flags

def test_DriveName():
  assert fs.Drive("C:").name == u"C:\\"

def test_DriveNameBack():
  assert fs.Drive("C:\\").name ==u"C:\\"

def test_DriveNameForward():
  assert fs.Drive("C:/").name==u"C:\\"

def test_DriveType():
  assert fs.Drive("C:").type==win32file.GetDriveTypeW("C:")

def test_Drive_as_String():
 assert unicode (fs.Drive("C:"))==u'Drive C:\\'
 
def test_DriveRoot():
  assert fs.Drive("C:").root() == fs.dir (u"C:\\")
  
def test_dir_copy_to_new_dir ():
  target_name = uuid.uuid1 ().hex
  source = os.path.join (TEST_ROOT, "a")
  target = os.path.join (TEST_ROOT, target_name)
  assert not os.path.isdir (target)
  fs.copy (source, target)
  assert dirs_are_equal (source, target)
  
if __name__ == "__main__":
  import nose
  nose.runmodule (exit=False) 
  raw_input ("Press enter...")
  