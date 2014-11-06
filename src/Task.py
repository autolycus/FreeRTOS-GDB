# File: Task.py
# Author: Carl Allendorph
# Date: 05NOV2014 
# 
# Description:
#  This file contains the implementation of a class to use for 
# inspecting the state of a FreeRTOS Task in GDB 
# 

import gdb

class TaskInspector:

  TCBType = gdb.lookup_type("TCB_t")

  def __init__(self, handle): 

    self._tcb = None
    if ( type(handle) == int ): 
      tcbPtr = gdb.Value(handle).cast(TaskInspector.TCBType.pointer())
      self._tcb = tcbPtr.dereference() 
    else: 
      try: 
        if ( handle.type == TaskInspector.TCBType ): 
          self._tcb = handle 

  def GetName(self): 
    return( self._tcb['pcTaskName'].string() )

  def GetPriority(self): 
    return ( self._tcb['uxPriority'] )

  def GetStackMargin(self):     
    topStack=task['pxTopOfStack']
    stackBase = task['pxStack']
    highWater = topStack - stackBase
    return(highWater)


  
