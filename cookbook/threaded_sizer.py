import os, sys
import threading
import Queue

from winsys import fs

def sizer (requests, results):
  while True:
    root = requests.get ()
    if root is None: 
      break
    results.put ((root, sum (f.size for f in fs.flat (root))))
    
if __name__ == '__main__':
  if len (sys.argv) > 1:
    root = fs.file (sys.argv[1])
  else:
    root = fs.file ("c:/temp")
    
  N_THREADS = 5
  requests = Queue.Queue ()
  results = Queue.Queue ()
  sizers = [threading.Thread (target=sizer, args=(requests, results)) for _ in range (N_THREADS)]
  for s in sizers:
    s.setDaemon (True)
    s.start ()

  dirs = set (d.filepath for d in root.dirs ())
  for dir in dirs:
    requests.put (dir)
    
  while True:
    dir, size = results.get ()
    print dir, "=>", size
    dirs.remove (dir)
    if not dirs:
      break
    
    if len (dirs) < 10:
      print "Waiting for:", ", ".join (dirs)
    else:
      print "Waiting for", len (dirs)

  for s in sizers:
    requests.put (None)
