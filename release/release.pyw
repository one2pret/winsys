import os, sys
import types
import wx

import releaselib

"""
+------------------------------------------------+
|Server / Database                               |
+------------------------------------------------+
|Directory Selection                             |
+------------------------+-----------------------+
|List of filenames       |Output Log             |
|                        |                       |
|                        |                       |
|                        |                       |
|                        |                       |
|                        |                       |
|                        |                       |
|                        |                       |
|                        |                       |
+------------------------+-----------------------+
|Buttons                                         |
+------------------------------------------------+
"""

class DelayedComboBox (wx.ComboBox):
  
  def __init__ (self, filler, *args, **kwargs):
    wx.ComboBox.__init__ (self, *args, **kwargs)
    self.filler = filler

    self.Bind (wx.EVT_SET_FOCUS, self.OnFocus)
    
  def OnFocus (self, event):
    if not self.Items:
      self.Value = "Please wait..."
      self.Items = self.filler ()

    event.Skip ()

class Frame (wx.Frame):

  def __init__ (self, release_filename, parent=None):
    wx.Frame.__init__ (self, parent, size=(600, 400))
    panel = wx.Panel (self)

    directory_label = wx.StaticText (panel, label="Directory")
    self.directory = wx.TextCtrl (panel, value="")
    directory_button = wx.Button (panel, size=(30, -1), label="...")
    server_label = wx.StaticText (panel, label="Server")
    self.server = DelayedComboBox (releaselib.servers, panel)
    db_label = wx.StaticText (panel, label="Database")
    self.db = wx.ComboBox (panel)
    self.checklist = wx.CheckListBox (panel)
    self.output = wx.TextCtrl (panel, style=wx.TE_MULTILINE)
    self.release_button = wx.Button (panel, label="Release")
    cancel_button = wx.Button (panel, id=wx.ID_CANCEL)

    h1 = wx.BoxSizer (wx.HORIZONTAL)
    h1.Add (directory_label, 0, wx.ALL, 5)
    h1.Add (self.directory, 1, wx.EXPAND | wx.ALL, 5)
    h1.Add (directory_button, 0, wx.ALL, 5)

    db_sizer = wx.BoxSizer (wx.HORIZONTAL)
    db_sizer.Add (server_label, 0, wx.ALL, 5)
    db_sizer.Add (self.server, 1, wx.EXPAND | wx.ALL, 5)
    db_sizer.Add (db_label, 0, wx.ALL, 5)
    db_sizer.Add (self.db, 1, wx.EXPAND | wx.ALL, 5)
    
    v1 = wx.BoxSizer (wx.VERTICAL)
    v1.Add (self.checklist, 1, wx.EXPAND | wx.ALL, 5)

    v2 = wx.BoxSizer (wx.VERTICAL)
    v2.Add (self.output, 1, wx.EXPAND | wx.ALL)

    h2 = wx.BoxSizer (wx.HORIZONTAL)
    h2.Add (v1, 4, wx.EXPAND | wx.ALL)
    h2.Add (v2, 5, wx.EXPAND | wx.ALL)

    h3 = wx.BoxSizer (wx.HORIZONTAL)
    h3.Add (self.release_button, 0, wx.ALL, 5)
    h3.Add (cancel_button, 0, wx.ALL,5)

    v3 = wx.BoxSizer (wx.VERTICAL)
    v3.Add (h1, 0, wx.EXPAND)
    v3.Add (db_sizer, 0, wx.EXPAND)
    v3.Add (h2, 1, wx.EXPAND)
    v3.Add (h3, 0)

    panel.SetSizer (v3)

    self.Centre ()
    self.Show (True)

    self.Bind (wx.EVT_BUTTON, self.OnDirectoryButton, id=directory_button.GetId ())
    self.Bind (wx.EVT_BUTTON, self.OnRelease, id=self.release_button.GetId ())
    self.Bind (wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
    
    self.Bind (wx.EVT_LISTBOX_DCLICK, self.OnCheckListDClick, id=self.checklist.GetId ())
    self.Bind (wx.EVT_CHECKLISTBOX, self.OnCheckListBox, id=self.checklist.GetId ())
    self.server.Bind (wx.EVT_KILL_FOCUS, self.OnServer)
    self.server.Bind (wx.EVT_TEXT, self.OnServer)
    #~ self.server.Bind (wx.EVT_SIZE, self.OnServer)
    
    self.AcceleratorTable = wx.AcceleratorTable (
      [
        (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL)
      ]
    )
    
    self.reset (release_filename)

  def reset (self, release_filename):
    if release_filename:
      release_filepath = os.path.abspath (release_filename)
      release_path = os.path.dirname (release_filepath)
      release_candidates = releaselib.get_release_candidates (release_path)
      release_directory = releaselib.find_release_directory (os.path.dirname (release_filepath))

      self.directory.SetValue (release_filepath)
      self.config = releaselib.ReleaseConfig (release_filename)
      self.checklist.SetItems (release_candidates)
      for i, filename in enumerate (release_candidates):
        if filename in self.config.filenames:
          self.checklist.Check (i)
    else:
      self.directory.SetValue (release_filename)
      self.checklist.Clear ()

    self.check_for_release ()

  def check_for_release (self):
    """Enable the [Release] button only if at least one
    item is checked"""
    for n, item in enumerate (self.checklist.GetStrings ()):
      if self.checklist.IsChecked (n):
        self.release_button.Enable (True)
        break
    else:
      self.release_button.Enable (False)

  def OnText (self, event):
    self.log ("OnText")
    self.log (event)
    event.Skip ()
    
  def OnServer (self, event):
    self.log ("OnServer")
    self.log (event)
    self.db.Clear ()
    self.db.Items = releaselib.databases (self.server.Value)
    event.Skip ()

  def OnCheckListBox (self, event):
    self.check_for_release ()
  
  def log (self, data, clear_first=False):
    if clear_first:
      self.output.Clear ()
    self.output.AppendText (unicode (data))
    self.output.AppendText ("\n")
  
  def OnCheckListDClick (self, event):
    self.log ("CheckList -> " + str (self.checklist.GetStringSelection ()))
    os.startfile (self.checklist.GetStringSelection ())
  
  def OnDirectoryButton (self, event):
    dlg = wx.FileDialog (
      self,
      "Choose a .release file",
      os.path.dirname (self.directory.GetValue () or os.getcwd ()),
      wildcard="*.release",
      style=wx.FD_FILE_MUST_EXIST | wx.FD_OPEN
    )
    try:
      if dlg.ShowModal () == wx.ID_OK:
        self.reset (dlg.GetPaths ()[0])
    finally:
      dlg.Destroy ()

  def OnRelease (self, event):
    self.log (self.AcceleratorTable)
    for i, filename in enumerate (self.checklist.GetStrings ()):
      if self.checklist.IsChecked (i):
        self.log ("%d: %s" % (i, filename))
    self.log ("Released!")

  def OnCancel (self, event):
    wx.Exit ()
    
class ReleaseApp (wx.App):
  
  def __init__ (self, release_filename, *args, **kwargs):
    self.release_filename = release_filename
    wx.App.__init__ (self, *args, **kwargs)

  def OnInit (self):
    frame = Frame (self.release_filename)
    return True

if __name__ == '__main__':
  if len (sys.argv) > 1:
    release_filename = sys.argv[1]
  else:
    release_filename = ""
  app = ReleaseApp (release_filename, filename="c:/temp/wx.log")
  app.MainLoop ()
