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

class StdTypes:
  uint32_t = gdb.lookup_type("uint32_t")
  uint16_t = gdb.lookup_type("uint16_t")


class QueueInspector: 
  def __init__(self): 
    """
    """

    pass

class HandleRegistry: 
  def __init__(self, regSymbol = "xQueueRegistry"):
    symbol, methodObj = gdb.lookup_symbol(regSymbol)
    self._registry = symbol.value()
    self._minIndex  = 0
    self._maxIndex = 0
    self._minIndex, self._maxIndex = self._registry.type.range()

  def GetName(self, handle):
    """ Find the string name associated with a queue 
        handle if it exists in the registry 
    """
    for i in range(self._minIndex, self._maxIndex):
      elem = self._registry[i]
      h = elem['xHandle']
      val = h.cast(StdTypes.uint32_t)
      if ( handle == val ):
        print("Found Entry for: %x" % handle)
        name = elem['pcQueueName'].string()
        return(name)

  def PrintRegistry(self):
    for i in range(self._minIndex, self._maxIndex):
      elem = self._registry[i]
      h = elem['xHandle']
      if ( h != 0 ):
        name = elem['pcQueueName'].string()
        print("%d: %3s %16s" % (i, h, name))

class FRList: 
  """ Wrapper for Inspecting FreeRTOS List_t Objects
  """
  def __init__(self, symbolStr):
    """ Maintains a reference to a FreeRTOS List_t 
        Object and provides tools for inspecting 
        the values of the list. 
        @param symbolStr User passes either a string of the 
           symbol that we wish to monitor or a pointer reference
           encoded as an integer (hex or otherwise). 
           Example: FRList("xSuspendedTaskList") -> maps to the list of blocked tasks
           Example: FRList(0x20000ae4)  -> pointer to a list object, user must
              confirm that it is an actual List_t object otherwise, you 
              will just get garbage           
    """

    ListType = gdb.lookup_type("List_t")
    self._value = None

    try: 
      if ( symbolStr.type  == ListType):
        self._value = symbolStr
        return
    except Exception as exc: 
      pass 

    symbol,methodObj = gdb.lookup_symbol(symbolStr)

    if( symbol != None ): 
      self._value = symbol.value()
    else:
      # We didn't find the symbol so maybe its a int pointer ? 
      try: 
        ListTypePtr = ListType.pointer()
        addrInt = int(symbolStr, 0)
        print("list Addr: %s, addrInt: %s" % (symbolStr, str(addrInt)))
        ListValPtr = gdb.Value(addrInt).cast(ListTypePtr)
        self._value = ListValPtr.dereference()
      except Exception as exc:
        print("Failed to Convert Passed Symbol to List_t: %s, %s" % (symbolStr, str(exc) ) )
        return


  def GetElements(self, CastTypeStr = None, startElem = 1 ):
    """ Get the Elements of the list as an array of 
        gdb.Value type objects. 
        @param CastTypeStr string name of the type of object that 
          we will cast the void *pvOwner elements of the list to. 
          If None, we will simply cast to uint32_t and print these 
          as hex values.
    """
    if ( self._value != None ):

      CastType = None
      if ( CastTypeStr != None):
        try:
          CastType = gdb.lookup_type(CastTypeStr).pointer()
        except:
          print("Failed to find type: %s" % CastTypeStr)

      resp = [] 
      items = [] 
      numElems = self._value['uxNumberOfItems']
      index = self._value['pxIndex']
        
      if ( startElem == 0 ):
        curr = index
      else:
        curr = index['pxPrevious']

      for i in range(0, numElems):
        owner = curr['pvOwner']

        if ( CastType != None ):
          castObjPtr = owner.cast(CastType)
          castObj = castObjPtr.dereference()
          resp.append(castObj)
        else:     
          ownerUInt = owner.cast(StdTypes.uint32_t)      
          resp.append(ownerUInt)
          
        itemVal = curr['xItemValue']
        items.append( itemVal.cast(StdTypes.uint32_t))

        curr = curr['pxPrevious']

      return(resp, items)
      
    else:
      raise ValueError("Invalid List Object - Possibly Failed to Initialize!")
    

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
ShowFRList()
ShowTaskList()
ShowHandleName()
