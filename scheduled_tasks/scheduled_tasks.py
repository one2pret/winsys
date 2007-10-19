import os, sys
import datetime
import time

import pythoncom
from win32com.taskscheduler import taskscheduler

def _set (obj, key, value):
  obj.__dict__[key] = value

class Constants (object):
  def __init__ (self):
    pass
constants = Constants ()
constants.__dict__.update (
  (name, getattr (taskscheduler, name)) 
    for name in dir (taskscheduler) 
    if name.isupper ()
)

def pytime_to_datetime (pytime):
  return datetime.datetime.fromtimestamp (int (pytime))
  
def datetime_to_pytime (timestamp):
  return pywintypes.Time (time.mktime (timestamp.timetuple ()))
  
def flag_to_word (number, prefix):
  for name in (k for k in dir (taskscheduler) if k.startswith (prefix)):
    if getattr (taskscheduler, name) == number:
      return name[len (prefix):].lower ()

def flags_to_words (number, prefix):
  words = set ()
  for flag_name in (k for k in dir (taskscheduler) if k.startswith (prefix)):
    flag_value = getattr (taskscheduler, flag_name)
    if flag_value & flags_as_number:
      words.add (flag_name[len (prefix):].lower ())
  return words

class Trigger (object):
  
  def __init__ (self, trigger, task=None):
    _set (self, "trigger", trigger)
    _set (self, "task", task)
    
  def __getattr__ (self, attr):
    trigger = self.trigger.GetTrigger ()
    return getattr (trigger, attr)
    
  def __setattr__ (self, attr, value):
    trigger = self.trigger.GetTrigger ()
    setattr (trigger, attr, value)
    
  def __str__ (self):
    return self.trigger.GetTriggerString ()
    
  def save (self):
    self.trigger.SetTrigger (self.
    trigger = self.trigger.GetTrigger ()
    trigger.QueryInterface (pythoncom.IID_IPersistFile).Save (None, 1)
    
class Triggers (object):
  
  def __init__ (self, task):
    self.task = task
    
  def __len__ (self):
    return self.task.GetTriggerCount ()
    
  def __getitem__ (self, item):
    return self.get_trigger (item)

  def __iter__ (self):
    for n_trigger in range (self.task.GetTriggerCount ()):
      yield self.get_trigger (n_trigger)
      
  def get_trigger (self, n_trigger):
    return Trigger (self.task.GetTrigger (n_trigger), self)
    
  def add (self):
    n_trigger, trigger = self.task.CreateTrigger ()
    return Trigger (trigger)

class Task (object):

  def __init__ (self, name, task, **kwargs):
    self.name = name
    self.task = task
    for k, v in kwargs.items ():
      setattr (self, k, v)

  def get_application_name (self):
    return self.task.GetApplicationName ()
  def set_application_name (self, application_name):
    self.task.SetApplicationName (application_name)
  application_name = property (get_application_name, set_application_name)
  
  def get_parameters (self):
    return self.task.GetParameters ()
  def set_parameters (self, parameters):
    self.task.SetParameters (parameters)
  parameters = property (get_parameters, set_parameters)
  
  def get_working_directory (self):
    return self.task.GetWorkingDirectory ()
  def set_working_directory (self, working_directory):
    self.task.SetWorkingDirectory (working_directory)
  working_directory = property (get_working_directory, set_working_directory)
  
  def get_priority (self):
    return self.task.GetPriority ()
  def set_priority (self, priority):
    self.task.SetPriority (priority)
  priority = property (get_priority, set_priority)
  
  @staticmethod
  def words_to_flags (flags_as_words):
    PREFIX = "TASK_FLAG_"
    flags = 0
    for word in flags_as_words:
      flags |= getattr (taskscheduler, PREFIX + word.upper ())
    return flags
  
  def get_task_flags (self):
    return flags_to_words (self.task.GetTaskFlags (), prefix="TASK_FLAG_")
  def set_task_flags (self, task_flags):
    try:
      flags = int (task_flags)
    except (ValueError, TypeError):
      flags = self.words_to_flags (task_flags)
    self.task.SetTaskFlags (flags)
  task_flags = property (get_task_flags, set_task_flags)
  
  def get_max_run_time (self):
    return self.task.GetMaxRunTime ()
  def set_max_run_time (self, max_run_time):
    self.task.SetMaxRunTime (max_run_time)
  max_run_time = property (get_max_run_time, set_max_run_time)
  
  def get_comment (self):
    return self.task.GetComment ()
  def set_comment (self, comment):
    self.task.SetComment (comment)
  comment = property (get_comment, set_comment)
  
  def get_creator (self):
    return self.task.GetCreator ()
  def set_creator (self, creator):
    self.task.SetCreator (creator)
  creator = property (get_creator, set_creator)
  
  def get_account_information (self):
    return self.task.GetAccountInformation ()
  def set_account_information (self, account_name_password):
    self.task.SetAccountInformation (*account_name_password)
  account_information = property (get_account_information, set_account_information)
  
  def get_work_item_data (self):
    return self.task.GetWorkItemData ()
  def set_work_item_data (self, data):
    self.task.SetWorkItemData (data)
  work_item_data = property (get_work_item_data, set_work_item_data)
  
  def get_next_run_time (self):
    return pytime_to_datetime (self.task.GetNextRunTime ())
  next_run_time = property (get_next_run_time)
  
  def get_most_recent_run_time (self):
    return pytime_to_datetime (self.task.GetMostRecentRunTime ())
  most_recent_run_time = property (get_most_recent_run_time)
  
  def run_times (self, n_to_fetch=1):
    return [pytime_to_datetime (run_time) for run_time in self.task.GetRunTimes (n_to_fetch)]
  
  def get_idle_wait (self):
    return self.task.GetIdleWait ()
  def set_idle_wait (self, idle_wait_and_deadline_mins):
    self.task.SetIdleWait (*idle_wait_and_deadline_mins)
  idle_wait = property (get_idle_wait, set_idle_wait)
  
  def get_status (self):
    return flag_to_word (self.task.GetStatus (), "SCHED_S_")
  status = property (get_status)
  
  def get_exit_code (self):
    return self.task.GetExitCode ()
  exit_code = property (get_exit_code)
  
  def get_triggers (self):
    return Triggers (self)
  triggers = property (get_triggers)
  
  def __getattr__ (self, attr):
    return getattr (self.task, attr)
  
  def __str__ (self):
    return "<Task: %s>" % self.name
    
  def save (self):
    self.task.QueryInterface (pythoncom.IID_IPersistFile).Save (None, 1)
  
class Tasks (object):
  
  def __init__ (self, computer=""):
    self.tasks = pythoncom.CoCreateInstance (
      taskscheduler.CLSID_CTaskScheduler,
      None,
      pythoncom.CLSCTX_INPROC_SERVER,
      taskscheduler.IID_ITaskScheduler
    )
    if computer:
      self.tasks.SetTargetComputer (computer)
    
  def __iter__ (self):
    for name in self.tasks.Enum ():
      yield Task (name, self.tasks.Activate (name))

  def __getitem__ (self, name):
    return self.get (name)

  def get (self, name):
    return Task (name, self.tasks.Activate (name))
  
  def add (self, name, **kwargs):
    task = self.tasks.NewWorkItem (name)
    return Task (name, task, **kwargs)
    
  def remove (self, name):
    self.tasks.Delete (name)
  
def task (name):
  return tasks ().get (name)

def tasks ():
  return Tasks ()
  
def add (name, **kwargs):
  return tasks ().add (name, **kwargs)
  
def remove (name):
  return tasks ().remove (name)
