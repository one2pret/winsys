import os, sys
import tempfile
import traceback
import types
import wx
import wx.richtext as rt

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
    value = self.Value
    self.Value = "Please wait..."
    self.Items = self.filler ()
    if value in self.Items:
      self.Value = value
    else:
      self.Value = ""
      
    event.Skip ()

class Frame (wx.Frame):

  def __init__ (self, release_filename, parent=None):
    wx.Frame.__init__ (self, parent, size=(800, 600))
    panel = wx.Panel (self)

    self.release_filename = release_filename or ""
    
    self.do_script_to = wx.CheckBox (panel)
    script_to_label = wx.StaticText (panel, label="Script to")
    self.script_to = wx.TextCtrl (parent=panel, value="")
    self.script_to_button = wx.Button (panel, size=(24, 20), label="...")
    
    self.do_compile_to = wx.CheckBox (panel)
    compile_to_label = wx.StaticText (panel, label="Compile first")
    
    server_label = wx.StaticText (panel, label="Server")
    self.server = DelayedComboBox (self.servers, panel)
    db_label = wx.StaticText (panel, label="Database")
    self.db = DelayedComboBox (self.databases, panel)
    username_label = wx.StaticText (panel, label="Username")
    self.username = wx.TextCtrl (parent=panel, value="")
    password_label = wx.StaticText (panel, label="Password")
    self.password = wx.TextCtrl (parent=panel, value="", style=wx.TE_PASSWORD)
    
    self.directory = wx.TextCtrl (parent=panel, value="")
    directory_button = wx.Button (panel, size=(24, 20), label="...")
    
    self.checklist = wx.CheckListBox (panel, style=wx.LB_EXTENDED)
    self.output = rt.RichTextCtrl (parent=panel, style=wx.TE_MULTILINE)
    self.release_button = wx.Button (panel, label="Release")
    cancel_button = wx.Button (panel, label="Close", id=wx.ID_CANCEL)

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
    h_database.Add (username_label, 0, wx.ALL, 5)
    h_database.Add (self.username, 1, wx.EXPAND | wx.ALL, 5)
    h_database.Add (password_label, 0, wx.ALL, 5)
    h_database.Add (self.password, 1, wx.EXPAND | wx.ALL, 5)
    
    v_checklist = wx.BoxSizer (wx.VERTICAL)
    v_checklist.Add (h_directory, 0, wx.EXPAND, 0)
    v_checklist.Add (self.checklist, 1, wx.EXPAND | wx.ALL, 3)

    v_output = wx.BoxSizer (wx.VERTICAL)
    v_output.Add (self.output, 1, wx.EXPAND | wx.ALL, 3)

    h2 = wx.BoxSizer (wx.HORIZONTAL)
    h2.Add (v_checklist, 1, wx.EXPAND | wx.ALL)
    h2.Add (v_output, 2, wx.EXPAND | wx.ALL)

    h_buttons = wx.BoxSizer (wx.HORIZONTAL)
    h_buttons.Add (cancel_button, 0, wx.ALL,5)
    h_buttons.Add (self.release_button, 0, wx.ALL, 5)
    
    v3 = wx.BoxSizer (wx.VERTICAL)
    v3.Add (h_database, 0, wx.EXPAND)
    v3.Add (h_script_to, 0, wx.EXPAND)
    v3.Add (h2, 1, wx.EXPAND)
    v3.Add (h_buttons, 0, wx.ALIGN_RIGHT)

    panel.SetSizer (v3)

    self.Centre ()
    self.Show (True)

    self.Bind (wx.EVT_CHECKBOX, self.check_for_script_to, id=self.do_script_to.Id)
    self.Bind (wx.EVT_CHECKBOX, self.check_for_compile_to, id=self.do_compile_to.Id)
    self.Bind (wx.EVT_BUTTON, self.OnScriptToButton, id=self.script_to_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnDirectoryButton, id=directory_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnRelease, id=self.release_button.Id)
    self.Bind (wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
    
    self.Bind (wx.EVT_LISTBOX_DCLICK, self.OnCheckListDClick, id=self.checklist.Id)
    self.Bind (wx.EVT_CHECKLISTBOX, self.OnCheckListBox, id=self.checklist.Id)
    self.checklist.Bind (wx.EVT_RIGHT_DOWN, self.OnDragInit)
    
    self.AcceleratorTable = wx.AcceleratorTable (
      [
        (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CANCEL)
      ]
    )
    
    self._servers = None
    
    self.reset (release_filename)

  def reset (self, release_filename):
    if release_filename:
      self.config = releaselib.ReleaseConfig (release_filename)
      self.script_to.Value = self.config.script_to or releaselib.find_release_directory (os.path.dirname (self.release_filename)) or ""
      self.server.Value = self.config.server or DEFAULT_SERVER
      self.db.Value = self.config.database or DEFAULT_DB
      self.username.Value = self.config.username or ""
      self.password.Value = self.config.password or ""
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

  def servers (self):
    if self._servers is None:
      self._servers = releaselib.servers ()
    return self._servers
    
  def databases (self):
    return releaselib.databases (self.server.Value)
  
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

  def OnServerChange (self, event):
    db_value = self.db.Value
    self.db.Items = releaselib.databases (self.server.Value)
    if db_value in self.db.Items:
      self.db.Value = db_value
    else:
      self.db.Value = ""
    event.Skip ()
    
  def OnCheckListBox (self, event):
    self.check_for_release ()
  
  def log_traceback (self):
    self.output.Newline ()
    self.output.BeginBold ()
    self.output.AppendText (unicode (traceback.format_exc ()))
    self.output.EndBold ()
    self.output.Newline ()
  
  def log (self, data, clear_first=False):
    if clear_first:
      self.output.Clear ()
    self.output.AppendText (unicode (data))
    self.output.AppendText ("\n")
  
  def OnCheckListDClick (self, event):
    for item in self.checklist.Selections:
      filename = self.checklist.GetString (item)
      os.startfile (os.path.join (self.directory.Value, filename))
  
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
    filenames = [os.path.join (self.directory.Value, f) for i, f in enumerate (self.checklist.GetStrings ()) if self.checklist.IsChecked (i)]
    
    self.log ("Release", clear_first=True)
    try:
      if self.do_compile_to.IsChecked ():
        self.log ("\nCompiling to: %s on %s" % (self.db.Value, self.server.Value))
        releaselib.release_objects ((self.server.Value, self.db.Value, self.username.Value, self.password.Value), filenames, self.log)
      
      if self.do_script_to.IsChecked ():
        self.log ("\nScripting to: %s" % self.script_to.Value)
        affected_objects = releaselib.affected_objects (filenames)
        released_filenames = releaselib.rescript_objects (
          (self.server.Value, self.db.Value, self.username.Value, self.password.Value), 
          affected_objects, 
          self.script_to.Value, 
          self.log
        )
        for filename in released_filenames:
          self.log ("  -> %s" % filename)
        
        heat_call = self.config.heat_call ()
        if heat_call:
          commit_summary = "Release package for HEAT #%d" % heat_call
        else:
          commit_summary = "Release package for %s" % self.directory.Value
        commit_summary += "\n\nObjects affected:\n  %s\n\n" % "\n  ".join (name for type, name, table in affected_objects)
          
        if self.config.comment_in:
          comment_in_filename = os.path.join (self.directory.Value, self.config.comment_in)
          try:
            commit_summary += "---\n\n%s" % open (comment_in_filename).read ()
          except IOError:
            self.log ("Couldn't find %s. Ignoring." % comment_in_filename)

        self.log ("\nCommit message:\n\n%s" % commit_summary)
        releaselib.commit_objects (released_filenames, commit_summary)

    except:
      self.log_traceback ()
    else:
      self.do_script_to.Value = 0
      self.do_compile_to.Value = 0
      self.check_for_release ()

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
  
  log_filename = os.path.join (tempfile.gettempdir (), "wx.log")
  try:
    open (log_filename, "w").close ()
  except IOError:
    app = ReleaseApp (release_filename, redirect=False)
  else:
    app = ReleaseApp (release_filename, redirect=True, filename=log_filename)
  
  app.MainLoop ()
