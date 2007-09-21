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
    directory_button = wx.Button (panel, size=(24, 20), label="...")
    
    self.do_script_to = wx.CheckBox (panel)
    script_to_label = wx.StaticText (panel, label="Script to")
    self.script_to = wx.TextCtrl (panel, value="")
    self.script_to_button = wx.Button (panel, size=(24, 20), label="...")
    
    server_label = wx.StaticText (panel, label="Server")
    self.server = DelayedComboBox (releaselib.servers, panel)
    db_label = wx.StaticText (panel, label="Database")
    self.db = wx.ComboBox (panel)
    
    self.checklist = wx.CheckListBox (panel)
    self.output = wx.TextCtrl (panel, style=wx.TE_MULTILINE)
    self.release_button = wx.Button (panel, label="Release")
    cancel_button = wx.Button (panel, id=wx.ID_CANCEL)

    h_directory = wx.BoxSizer (wx.HORIZONTAL)
    h_directory.Add (directory_label, 0, wx.ALL, 5)
    h_directory.Add (self.directory, 1, wx.EXPAND | wx.ALL, 5)
    h_directory.Add (directory_button, 0, wx.ALL, 5)
    
    h_script_to = wx.BoxSizer (wx.HORIZONTAL)
    h_script_to.Add (self.do_script_to, 0, wx.ALL, 5)
    h_script_to.Add (script_to_label, 0, wx.ALL, 5)
    h_script_to.Add (self.script_to, 1, wx.EXPAND | wx.ALL, 5)
    h_script_to.Add (self.script_to_button, 0, wx.ALL, 5)

    h_database = wx.BoxSizer (wx.HORIZONTAL)
    h_database.Add (server_label, 0, wx.ALL, 5)
    h_database.Add (self.server, 1, wx.EXPAND | wx.ALL, 5)
    h_database.Add (db_label, 0, wx.ALL, 5)
    h_database.Add (self.db, 1, wx.EXPAND | wx.ALL, 5)
    
    v_checklist = wx.BoxSizer (wx.VERTICAL)
    v_checklist.Add (self.checklist, 1, wx.EXPAND | wx.ALL, 3)

    v_output = wx.BoxSizer (wx.VERTICAL)
    v_output.Add (self.output, 1, wx.EXPAND | wx.ALL, 3)

    h2 = wx.BoxSizer (wx.HORIZONTAL)
    h2.Add (v_checklist, 1, wx.EXPAND | wx.ALL)
    h2.Add (v_output, 1, wx.EXPAND | wx.ALL)

    h_buttons = wx.BoxSizer (wx.HORIZONTAL)
    h_buttons.Add (cancel_button, 0, wx.ALL,5)
    h_buttons.Add (self.release_button, 0, wx.ALL, 5)
    
    v3 = wx.BoxSizer (wx.VERTICAL)
    v3.Add (h_directory, 0, wx.EXPAND)
    v3.Add (h_script_to, 0, wx.EXPAND)
    v3.Add (h_database, 0, wx.EXPAND)
    v3.Add (h2, 1, wx.EXPAND)
    v3.Add (h_buttons, 0, wx.ALIGN_RIGHT)

    panel.SetSizer (v3)

    self.Centre ()
    self.Show (True)

    self.Bind (wx.EVT_BUTTON, self.OnDirectoryButton, id=directory_button.Id)
    self.Bind (wx.EVT_CHECKBOX, self.check_for_script_to, id=self.do_script_to.Id)
    self.Bind (wx.EVT_BUTTON, self.OnScriptToButton, id=self.script_to_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnRelease, id=self.release_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
    
    self.Bind (wx.EVT_LISTBOX_DCLICK, self.OnCheckListDClick, id=self.checklist.Id)
    self.Bind (wx.EVT_CHECKLISTBOX, self.OnCheckListBox, id=self.checklist.Id)
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
    self.check_for_script_to ()

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
      os.path.dirname (self.directory.Value or os.getcwd ()),
      wildcard="*.release",
      style=wx.FD_FILE_MUST_EXIST | wx.FD_OPEN
    )
    try:
      if dlg.ShowModal () == wx.ID_OK:
        self.reset (dlg.Path)
    finally:
      dlg.Destroy ()

  def check_for_script_to (self, event=None):
    self.script_to.Enable (self.do_script_to.IsChecked ())
    self.script_to_button.Enable (self.do_script_to.IsChecked ())
  
  def OnScriptToButton (self, event):
    dlg = wx.DirDialog (
      self,
      "Choose a folder to script to",
      os.path.dirname (self.script_to.Value or os.getcwd ()),
      style=wx.DD_DIR_MUST_EXIST | wx.DD_DEFAULT_STYLE
    )
    try:
      if dlg.ShowModal () == wx.ID_OK:
        self.script_to.Value = dlg.Path
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
  app = ReleaseApp (release_filename, filename="wx.log")
  app.MainLoop ()
