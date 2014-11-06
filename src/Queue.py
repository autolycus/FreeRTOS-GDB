# File: Queue.py 
# Author: Carl Allendorph
# Date: 05NOV2014 
# 
# Description: 
#   This file contains the implementation of a Queue Inspector 
# class.
# 

import gdb 


class QueueInspector: 
  def __init__(self, handle): 
    """
    """
    QueueType = gdb.lookup_type("Queue_t")
    self._queue = gdb.Value(handle).cast(QueueType)

  def GetTasksWaitingToSend(self): 
    """
    """
    sendList = ListInspector(self._queue['xTasksWaitingToSend'])

    return( sendList.GetElements(
    pass

  def GetTasksWaitingToReceive(self): 
    """
    """
    pass 

  def GetQueueMessagesWaiting(self):
    """
    """
    pass

  def GetQueueType(self): 
    """
    """
    pass 

