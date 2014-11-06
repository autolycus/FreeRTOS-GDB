# File: List.py
# Author: Carl Allendorph
# Date: 05NOV2014 
#
# Description: 
#   This file contains the class for inspecting 
# a FreeRTOS List Object
# 


import gdb 

from Types import StdTypes

class ListInspector: 
  """ FreeRTOS List Inspector Object
  """ 

  ListType = gdb.lookup_type("List_t")

  def __init__(self, handle ): 
    """
    """ 
    self._list = None

    self.assign(handle)

  def Assign(self, listObj): 
    try: 
      if ( listObj.type == ListInspector.ListType ): 
        self._list = listObj
        return
      else: 
        raise TypeError("Invalid List Object Type!")
    except Exception as exc: 
      print(" Failed to assign from List object: %s" % str(exc))
      
    symbol, methodObj = gdb.lookup_symbol(listObj)
    if ( symbol != None ): 
      self._list = symbol.value() 
    else:       
      addrInt = int(listObj, 0)
      listObjPtr = gdb.Value(addrInt).cast(ListInspector.ListType.pointer())
      self._list = listObjPtr.dereference()


      
  def GetElements(self, CastTypeStr = None, startElem = 1 ): 
    """ Get the Elements of the list as an array of 
        gdb.Value type objects. 
        @param CastTypeStr string name of the type of object that 
          we will cast the void *pvOwner elements of the list to. 
          If None, we will simply cast to uint32_t and print these 
          as hex values.
        @param startElem This is a flag to indicate whether 
           we will start getting elements starting at 0 or 1. Note
           that this is to deal with some non-consistent behavior 
           of some of the TCB Task lists.
    """
    if ( self._list != None ):

      CastType = None
      if ( CastTypeStr != None):
        try:
          CastType = gdb.lookup_type(CastTypeStr).pointer()
        except:
          print("Failed to find type: %s" % CastTypeStr)

      resp = [] 
      numElems = self._list['uxNumberOfItems']
      index = self._list['pxIndex']
        
      if ( startElem == 0 ):
        curr = index
      else:
        curr = index['pxPrevious']

      for i in range(0, numElems):
        owner = curr['pvOwner']


        ownerObj = None
        if ( CastType != None ):
          castObjPtr = owner.cast(CastType)
          castObj = castObjPtr.dereference()
          ownerObj = castObj
        else:     
          ownerUInt = owner.cast(StdTypes.uint32_t)      
          ownerObj = ownerUInt          
          
        itemVal = curr['xItemValue']
        resp.append( (ownerObj, itemVal.case(StdTypes.uint32_t)) )

        curr = curr['pxPrevious']

      return(resp)
      
    else:
      raise ValueError("Invalid List Object - Possibly Failed to Initialize!")
    
