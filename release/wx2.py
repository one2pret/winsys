import os
import wx

import releaselib

"""
+------------------------+-----------------------+
|Directory Selection     |Output Log             |
+------------------------+                       |
|List of filenames       |                       |
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

class Frame (wx.Frame):

  def __init__ (self, parent=None):
    wx.Frame.__init__ (self, parent, size=(600, 400))
    panel = wx.Panel (self)

    directory_label = wx.StaticText (panel, label="Directory")
    self.directory = wx.TextCtrl (panel, value="")
    directory_button = wx.Button (panel, size=(30, -1), label="...")
    self.checklist = wx.CheckListBox (panel)
    self.output = wx.TextCtrl (panel, style=wx.TE_MULTILINE)
    release_button = wx.Button (panel, label="Release")
    cancel_button = wx.Button (panel, id=wx.ID_CANCEL)

    h1 = wx.BoxSizer (wx.HORIZONTAL)
    h1.Add (directory_label, 0, wx.ALL, 5)
    h1.Add (self.directory, 1, wx.EXPAND | wx.ALL, 5)
    h1.Add (directory_button, 0, wx.ALL, 5)

    v1 = wx.BoxSizer (wx.VERTICAL)
    v1.Add (h1, 0, wx.EXPAND)
    v1.Add (self.checklist, 1, wx.EXPAND | wx.ALL, 5)

    v2 = wx.BoxSizer (wx.VERTICAL)
    v2.Add (self.output, 1, wx.EXPAND | wx.ALL)

    h2 = wx.BoxSizer (wx.HORIZONTAL)
    h2.Add (v1, 1, wx.EXPAND | wx.ALL, 3)
    h2.Add (v2, 1, wx.EXPAND | wx.ALL, 3)

    h3 = wx.BoxSizer (wx.HORIZONTAL)
    h3.Add (release_button, 0, wx.ALL, 5)
    h3.Add (cancel_button, 0, wx.ALL,5)

    v3 = wx.BoxSizer (wx.VERTICAL)
    v3.Add (h2, 1, wx.EXPAND)
    v3.Add (h3, 0)

    panel.SetSizer (v3)

    self.Centre ()
    self.Show (True)

    self.Bind (wx.EVT_BUTTON, self.OnDirectoryButton, id=directory_button.GetId ())
    self.Bind (wx.EVT_BUTTON, self.OnRelease, id=release_button.GetId ())
    self.Bind (wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)


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
        self.directory.SetValue (dlg.GetPaths ()[0])
        self.config = releaselib.ReleaseConfig (self.directory.GetValue ())
        self.checklist.SetItems (self.config.filenames)
    finally:
      dlg.Destroy ()

  def OnRelease (self, event):
    wx.MessageBox("Released!")

  def OnCancel (self, event):
    wx.Exit ()

if __name__ == '__main__':
  app = wx.App(filename="c:/temp/wx.log")
  frame = Frame ()
  app.MainLoop ()
