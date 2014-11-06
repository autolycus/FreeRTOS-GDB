# File: GDBCommands.py
# Author: Carl Allendorph
# Date: 05NOV2014 
# 
# Description: 
#   This file contains the implementation of some custom 
# GDB commands for Inspecting the FreeRTOS state


import gdb


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




class ShowList(gdb.Command):
  """ Generate a print out of the elements in a list 
      passed to this command. User must pass a symbol that 
      will be looked up. 
  """

  def __init__(self):
    super(ShowFRList, self).__init__(
      "show List-Handle", 
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
