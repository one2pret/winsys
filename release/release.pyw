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

DEFAULT_SERVER = "VODEV1"
DEFAULT_DB = "DEV"

class DelayedComboBox (wx.ComboBox):
  
  def __init__ (self, filler, *args, **kwargs):
    wx.ComboBox.__init__ (self, *args, **kwargs)
    self.filler = filler

    self.Bind (wx.EVT_SET_FOCUS, self.OnFocus)
    
  def OnFocus (self, event):
    if not self.Items:
      self.Value = "Please wait..."
      values = self.filler ()
      self.Items = self.filler ()

    #~ event.Skip ()

class TextCtrl (wx.TextCtrl):
  
  def __init__ (self, on_change, *args, **kwargs):
    wx.TextCtrl.__init__ (self, *args, **kwargs)
    self.on_change = on_change
    self.old_value = None
    
    self.Bind (wx.EVT_SET_FOCUS, self.OnFocus)
    self.Bind (wx.EVT_KILL_FOCUS, self.OnBlur)
    
  def OnFocus (self, event):
    self.old_value = self.Value
    event.Skip ()
    
  def OnBlur (self, event):
    if self.on_change and self.Value <> self.old_value:
      self.on_change (self.Value)
    self.old_value = None
    event.Skip ()

class Frame (wx.Frame):

  def __init__ (self, release_filename, parent=None):
    wx.Frame.__init__ (self, parent, size=(600, 400))
    panel = wx.Panel (self)

    #~ specfile_label = wx.StaticText (panel, label="Release spec")
    #~ self.specfile = TextCtrl (self.OnSpecfileChange, parent=panel, value="")
    #~ specfile_button = wx.Button (panel, size=(24, 20), label="...")
    
    self.release_filename = release_filename or ""
    
    self.do_script_to = wx.CheckBox (panel)
    script_to_label = wx.StaticText (panel, label="Script to")
    self.script_to = TextCtrl (self.log, parent=panel, value="")
    self.script_to_button = wx.Button (panel, size=(24, 20), label="...")
    
    self.do_compile_to = wx.CheckBox (panel)
    compile_to_label = wx.StaticText (panel, label="Compile first")
    
    server_label = wx.StaticText (panel, label="Server")
    self.server = DelayedComboBox (releaselib.servers, panel)
    db_label = wx.StaticText (panel, label="Database")
    self.db = wx.ComboBox (panel)
    
    self.directory = TextCtrl (self.log, parent=panel, value="")
    directory_button = wx.Button (panel, size=(24, 20), label="...")
    
    self.checklist = wx.CheckListBox (panel, style=wx.LB_EXTENDED)
    self.output = TextCtrl (self.log, parent=panel, style=wx.TE_MULTILINE)
    self.release_button = wx.Button (panel, label="Release")
    cancel_button = wx.Button (panel, id=wx.ID_CANCEL)

    #~ h_specfile = wx.BoxSizer (wx.HORIZONTAL)
    #~ h_specfile.Add (specfile_label, 0, wx.ALL, 5)
    #~ h_specfile.Add (self.specfile, 1, wx.EXPAND | wx.ALL, 5)
    #~ h_specfile.Add (specfile_button, 0, wx.ALL, 5)
    
    h_directory = wx.BoxSizer (wx.HORIZONTAL)
    h_directory.Add (self.directory, 1, wx.EXPAND | wx.ALL, 3)
    h_directory.Add (directory_button, 0, wx.ALL, 3)
    
    h_script_to = wx.BoxSizer (wx.HORIZONTAL)
    h_script_to.Add (self.do_compile_to, 0, wx.ALL, 5)
    h_script_to.Add (compile_to_label, 0, wx.ALL, 5)
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
    v_checklist.Add (h_directory, 0, wx.EXPAND, 0)
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
    #~ v3.Add (h_specfile, 0, wx.EXPAND)
    v3.Add (h_database, 0, wx.EXPAND)
    v3.Add (h_script_to, 0, wx.EXPAND)
    v3.Add (h2, 1, wx.EXPAND)
    v3.Add (h_buttons, 0, wx.ALIGN_RIGHT)

    panel.SetSizer (v3)

    self.Centre ()
    self.Show (True)

    #~ self.Bind (wx.EVT_BUTTON, self.OnSpecfileButton, id=specfile_button.Id)
    self.Bind (wx.EVT_CHECKBOX, self.check_for_script_to, id=self.do_script_to.Id)
    self.Bind (wx.EVT_CHECKBOX, self.check_for_compile_to, id=self.do_compile_to.Id)
    self.Bind (wx.EVT_BUTTON, self.OnScriptToButton, id=self.script_to_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnDirectoryButton, id=directory_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnRelease, id=self.release_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
    
    self.Bind (wx.EVT_LISTBOX_DCLICK, self.OnCheckListDClick, id=self.checklist.Id)
    self.Bind (wx.EVT_CHECKLISTBOX, self.OnCheckListBox, id=self.checklist.Id)
    self.checklist.Bind (wx.EVT_RIGHT_DOWN, self.OnDragInit)
    self.server.Bind (wx.EVT_KILL_FOCUS, self.OnServer)
    self.server.Bind (wx.EVT_TEXT, self.OnServer)
    
    self.AcceleratorTable = wx.AcceleratorTable (
      [
        (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL)
      ]
    )
    
    self.reset (release_filename)

  def reset (self, release_filename):
    #~ self.specfile.Value = release_filename
    self.config = releaselib.ReleaseConfig (release_filename)
    if os.path.isfile (release_filename):
      self.script_to.Value = self.config.script_to or releaselib.find_release_directory (os.path.dirname (self.release_filename)) or ""
      self.server.Value = self.config.server or DEFAULT_SERVER
      self.db.Value = self.config.database or DEFAULT_DB
      self.directory.Value = self.config.directory or os.path.dirname (self.release_filename)

    else:
      self.log ("No such specfile")
      self.script_to.Value = ""
      self.server.Value = DEFAULT_SERVER
      self.db.Value = DEFAULT_DB
      self.directory.Value = ""

    self.SetLabel (release_filename or "<No specfile used>")
    self.populate_checklist ()
    self.check_for_script_to ()
    self.check_for_compile_to ()
    self.check_for_release ()

  def populate_checklist (self):
    self.checklist.Clear ()
    filenames = self.config.filenames = releaselib.get_release_candidates (self.directory.Value)
    self.checklist.SetItems (filenames)
    for i, filename in enumerate (filenames):
      if filename in filenames:
        self.checklist.Check (i)

  def check_for_release (self):
    """Enable the [Release] button only if at least one
    item is checked and at least one action checked."""
    if not any (button.IsChecked () for button in [self.do_script_to, self.do_compile_to]):
      self.release_button.Enable (False)
      return

    if not any (self.checklist.IsChecked (n) for n, item in enumerate (self.checklist.GetStrings ())):
      self.release_button.Enable (False)
      return

    self.release_button.Enable (True)

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
    for item in self.checklist.Selections:
      filename = self.checklist.GetString (item)
      self.log ("CheckList -> " + filename)
      os.startfile (os.path.join (self.directory.Value, filename))
  
  #~ def OnSpecfileChange (self, value):
    #~ self.reset (value)
  
  #~ def OnSpecfileButton (self, event):
    #~ dlg = wx.FileDialog (
      #~ self,
      #~ "Choose a .release file",
      #~ os.path.dirname (self.specfile.Value),
      #~ wildcard="*.release",
      #~ style=wx.FD_FILE_MUST_EXIST | wx.FD_OPEN
    #~ )
    #~ try:
      #~ if dlg.ShowModal () == wx.ID_OK:
        #~ self.OnSpecfileChange (dlg.Path)
    #~ finally:
      #~ dlg.Destroy ()

  def OnDirectoryButton (self, event):
    dlg = wx.DirDialog (
      self,
      "Choose a scripts folder",
      os.path.dirname (self.directory.Value + os.sep),
      style=wx.DD_DIR_MUST_EXIST | wx.DD_DEFAULT_STYLE
    )
    try:
      if dlg.ShowModal () == wx.ID_OK:
        self.directory.Value = dlg.Path
        self.populate_checklist ()
    finally:
      dlg.Destroy ()

  def check_for_script_to (self, event=None):
    self.script_to.Enable (self.do_script_to.IsChecked ())
    self.script_to_button.Enable (self.do_script_to.IsChecked ())
    self.check_for_release ()
  
  def check_for_compile_to (self, event=None):
    #~ self.server.Enable (self.do_compile_to.IsChecked ())
    #~ self.db.Enable (self.do_compile_to.IsChecked ())
    self.check_for_release ()
  
  def OnScriptToButton (self, event):
    dlg = wx.DirDialog (
      self,
      "Choose a folder to script to",
      os.path.dirname ((self.script_to.Value or releaselib.find_release_directory () or "") + os.sep),
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
    
  def OnDragInit(self, event):
    """ Begin a Drag Operation """
    selection = self.checklist.HitTest (event.Position)
    if selection not in self.checklist.Selections:
      self.checklist.DeselectAll ()
      self.checklist.Select (selection)
    tdo = wx.FileDataObject ()
    for selection in self.checklist.Selections:
      tdo.AddFile (os.path.join (self.directory.Value, self.checklist.GetString (selection)))
    tds = wx.DropSource (self.checklist)
    tds.SetData (tdo)
    tds.DoDragDrop (True)

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
  open ("wx.log", "w").close ()
  app = ReleaseApp (release_filename, filename="wx.log")
  app.MainLoop ()
