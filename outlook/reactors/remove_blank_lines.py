import re

depends_on = ["remove_sig"]
message_filter = None

SUBBERS = [
  (re.compile (r"((>|\s)*\r?\n){3,}", re.UNICODE), u"\n\n"),
  (re.compile (r"\s*[_-]*\s*$", re.UNICODE), u""),
  (re.compile (r"[_-]+\s*\n\s*[_-]+", re.UNICODE), u"-----------------"),
  (re.compile (r"^\s+", re.UNICODE), u"")
]

def process_message (message):
  for (look_for, replace_by) in SUBBERS:
    message.Text = look_for.sub (replace_by, message.Text)
