import re

message_filter = None

JUNK = [
  u"Don't waste paper. Think before you print.",
  u"""The contents of this e-mail are confidential to the ordinary user of 
  the e-mail address to which it was addressed, and may also be privileged. 
  If you are not the addressee of this e-mail you may not copy, forward, 
  disclose or otherwise use it or any part of it in any form whatsoever. 
  If you have received this e-mail in error, please e-mail the sender by 
  replying to this message. CBS Outdoor Ltd reserves the right to monitor 
  e-mail communications from external/internal sources for the purposes of 
  ensuring correct and appropriate use of CBS Outdoor facilities. CBS Outdoor 
  Limited, registered in England and Wales with company number 02866133 and 
  registered address at Camden Wharf, 28 Jamestown Road, London, NW1 7BY.""",
  u"<mailto:[^>]*>",
  u"Tim Golden Senior Analyst Programmer T: 020 7482 3000"
]

JUNK_MATCHERS = [re.compile (u"\\s+".join (j.split ()), re.UNICODE) for j in JUNK]

def process_message (message):  
  for junk_matcher in JUNK_MATCHERS:
    message.Text = junk_matcher.sub ("", message.Text.replace (u"\xff", u" "))
  return False
