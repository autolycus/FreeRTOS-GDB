# File: FreeRTOS.py
# Author: Carl Allendorph
# Date: 05NOV2014 
#
# Description:
#   This file contains some python code that utilizes the GDB API 
# to inspect information about the FreeRTOS internal state. The 
# idea is to provide the user with the ability to inspect information 
# about the tasks, queues, mutexs, etc. 
# 

import gdb
import pprint
from Types import StdTypes 
from List import ListInspector 
    

class Scheduler:
  
  def __init__(self): 
    
    self._blocked = FRList("xSuspendedTaskList")
    self._delayed1 = FRList("xDelayedTaskList1")
    self._delayed2 = FRList("xDelayedTaskList2")
    self._readyLists = []
    readyTasksListsStr = "pxReadyTasksLists"
    readyListsSym,methodType = gdb.lookup_symbol(readyTasksListsStr)
    if ( readyListsSym != None ): 
      readyLists = readyListsSym.value()
      minIndex, maxIndex = readyLists.type.range()
      for i in range(minIndex, maxIndex+1):
        readyList = readyLists[i]
        FRReadyList = FRList( readyList )
        self._readyLists.append(FRReadyList)
    else: 
      print("Failed to Find Symbol: %s" % readyTasksListsStr)
      raise ValueError("Invalid Symbol!")

  def ShowTaskList(self): 
    self.PrintTableHeader()
    for i,rlist in enumerate(self._readyLists):
      if i == 0:
        tasks,items = rlist.GetElements( "TCB_t", 0 )
      else: 
        tasks,items = rlist.GetElements( "TCB_t", 1 )
      if ( len(tasks) > 0 ): 
        print("Ready List {%d}: Num Tasks: %d" % (i, len(tasks)))
        for t in tasks:           
          self.PrintTaskFormatted(t)

    btasks,items = self._blocked.GetElements("TCB_t")
    print("Blocked List: Num Tasks: %d" % len(btasks))
    for t in btasks:           
      self.PrintTaskFormatted(t)

    d1tasks,items = self._delayed1.GetElements("TCB_t")
    print("Delayed {1}: Num Tasks: %d" % len(d1tasks))
    for i,t in enumerate(d1tasks):           
      self.PrintTaskFormatted(t,items[i])

    d2tasks,items = self._delayed2.GetElements("TCB_t")
    print("Delayed {2}: Num Tasks: %d" % len(d2tasks))
    for i,t in enumerate(d2tasks):           
      self.PrintTaskFormatted(t,items[i])


  def PrintTableHeader(self):
    print("%16s %3s %4s" % ("Name", "PRI", "STCK"))

  def PrintTaskFormatted(self, task, itemVal = None):
    topStack=task['pxTopOfStack']
    stackBase = task['pxStack']
    highWater = topStack - stackBase
    taskName = task['pcTaskName'].string()
    taskPriority = task['uxPriority']
    if ( itemVal != None ):
      print("%16s %3s %4s %5s" % (taskName, taskPriority, highWater, itemVal))
    else:
      print("%16s %3s %4s" % (taskName, taskPriority, highWater))

class ShowHandleName(gdb.Command):
  """ Generate a print out of the handle by name 
  """
  def __init__(self):
    super(ShowHandleName, self).__init__(
      "show Handle-Name",
      gdb.COMMAND_SUPPORT
      )

  def invoke(self, arg, from_tty):
    argv = gdb.string_to_argv(arg)
    if ( len(argv) != 1 ):
      print("Invalid Argument: Requires one handle arg")
    handle = int( argv[0], 0)
    reg = HandleRegistry()
    name = reg.GetName(handle)
    print("Handle 0x%08x: %s" % (handle, name))

class ShowRegistry(gdb.Command):
  """ Generate a print out of the queue handle registry
  """
  def __init__(self):
    super(ShowRegistry, self).__init__(
      "show Handle-Registry", 
      gdb.COMMAND_SUPPORT
      )
    
  def invoke(self, arg, from_tty):
    reg = HandleRegistry()
    reg.PrintRegistry()
    
class ShowTaskList(gdb.Command):
  """ Generate a print out of the current tasks and their states.
  """
  def __init__(self):
    super(ShowTaskList, self).__init__(
      "show Task-List", 
      gdb.COMMAND_SUPPORT
      )

  def invoke(self, arg, from_tty):
    sched = Scheduler()
    sched.ShowTaskList()




class ShowFRList(gdb.Command):
  """ Generate a print out of the elements in a list 
      passed to this command. User must pass a symbol that 
      will be looked up. 
  """

  def __init__(self):
    super(ShowFRList, self).__init__(
      "show FRList", 
      gdb.COMMAND_SUPPORT, 
      gdb.COMPLETE_SYMBOL
      )
      
  def invoke(self, arg, from_tty):
    argv = gdb.string_to_argv(arg)    

    CastTypeStr = None
    if ( len(argv) > 0):
      symbolArg = argv[0]
    
    if ( len(argv) > 1 ):
      CastTypeStr = argv[1]
      
    listVal = FRList(symbolArg)
    
    elems = listVal.GetElements( CastTypeStr )

    for  elem in elems :
      print("Elem: %s" % str(elem))


ShowRegistry()
ShowList()
ShowTaskList()
ShowHandleName()
