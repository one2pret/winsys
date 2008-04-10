import os, sys
import datetime
import re
from cStringIO import StringIO
from ConfigParser import SafeConfigParser

import sql

import outlook

message_filter = re.compile (r"\bHEAT:")

ATTACHMENTS_FOLDER = r"\\gb.vo.local\files\IT\IT\temp\heat-attachments"
HEAT_NUMBER = re.compile (r"\[(\d{5,8})\]")
ACK_TEXT = """Your email has been entered into our Helpdesk system and has a reference of %(call_id)s.

Please quote the reference number above when requesting further assistance with this job.

Whilst you are awaiting a response, please check the IT Tips pages on the Intranet . If you manage to resolve your problem, please let us know.

Regards
IT Helpdesk
"""

db = None
def init ():
  global db
  db = sql.pyodbc_connection ("VODEV1", "HEAT", autocommit=True)
  #~ db = pyodbc_connection ("VOREPORTS", "HEAT", "heat", "heat", autocommit=True)
  
def send_acknowledgement (call_id, message):
  outlook.send (
    message.Session,
    [message.Sender.Name], 
    "RE: %s [%s]" % (message.Subject, call_id),
    ACK_TEXT % locals ()
  )
  print "Sent to", message.Sender.Name

def read_attachments (call_id):  
  q = db.cursor ()
  q.execute (u"SELECT GDetail FROM heat.HEATGen WITH (NOLOCK) WHERE GName = ? AND GCode = 'AT'", [call_id])
  for text, in q.fetchall ():
    ini = ini_from_text (text)
    if "Attachments" in ini.sections ():
      for attachment_name, attachment_details in ini.items ("Attachments"):
        yield attachment_details.split ("|")
  q.close ()

def write_attachments (call_id, attachments):
  ini = SafeConfigParser ()
  ini.add_section ("Info")
  ini.set ("Info", "NumAttachments", str (len (attachments)))
  ini.add_section ("Attachments")
  for n_attachment, attachment in enumerate (attachments):
    ini.set ("Attachments", "Attachment%d" % n_attachment, "|".join (attachment))
  
  q = db.cursor ()
  q.execute (u"DELETE FROM heat.HEATGen WHERE GCode = 'AT' AND GName = ?", [call_id])
  q.execute (u"""
    INSERT INTO heat.HEATGen (GCode, GName, GType, GDetail, GDTLastMod) 
    VALUES ('AT', ?, '', ?, DATEDIFF (second, CONVERT (DATETIME, '19700101', 112), GETDATE ()))""",
    [call_id, ini_to_text (ini)]
  )
  q.close ()
  
def ini_from_text (text):
  ini = SafeConfigParser ()
  ifile = StringIO ()
  ifile.write (text)
  ifile.flush ()
  ifile.seek (0)
  ini.readfp (ifile)
  return ini
  
def ini_to_text (ini):
  ofile = StringIO ()
  ini.write (ofile)
  ofile.flush ()
  ofile.seek (0)
  return ofile.read ()

def update_attachments (call_id, message):
  attachments_folder = os.path.join (ATTACHMENTS_FOLDER, call_id)
  attachments = outlook.Collection (message.Attachments)
  if attachments:
    filed_attachments = []
    for attachment in attachments:
      if attachment.Type == outlook.constants.CdoFileData:
        if not os.path.exists (attachments_folder):
          os.mkdir (attachments_folder)
        attachment_filepath = os.path.join (attachments_folder, attachment.Name)
        attachment.WriteToFile (attachment_filepath)
        filed_attachments.append ((attachment.Name, attachment_filepath))    
    write_attachments (call_id, filed_attachments)

def create_new_call (message):
  sender = unicode (message.Sender.Name).encode ("utf8")
  subject = unicode (message.Subject).encode ("utf8")
  text = unicode (message.Text).encode ("utf8")

  q = db.cursor ()
  q.execute ("""EXECUTE pr_create_new_call
    @i_cust_name = ?,
    @i_call_subject = ?,
    @i_call_body = ?""",
    (sender, subject, text)
  )
  row = q.fetchone ()
  q.close ()
  call_id = row[0]
  
  update_attachments (call_id, message)
  send_acknowledgement (call_id, message)
  
def update_old_call (call_id, message):
  #
  # This is the hard part: try to pick out the part of the
  # message which is new. For the purposes of experimentation,
  # consider everything up to the first run of 5 dashes or underscores.
  #
  useful_text = re.match ("^(.*)([_-]{5,})?", message.Text).group (1).strip ()
  journal_text = "%s emailed:\r\n\r\n%s" % (message.Sender.Name, useful_text)
  journal_text = journal_text.strip ().encode ("utf8")
  call_id  = call_id.encode ("utf8")
  
  q = db.cursor ()
  q.execute ("EXECUTE pr_add_journal @i_call_id = ?, @i_entry_text = ?", 
    [call_id, journal_text]
  )
  q.close ()
  
  update_attachments (call_id, message)

def process_message (message):
  for call_id in HEAT_NUMBER.findall (message.Subject + " " + message.Text):
    update_old_call (call_id.zfill (8), message)
    break
  else:
    create_new_call (message)
