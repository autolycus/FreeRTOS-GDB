FreeRTOS-GDB
============

Python API Library for inspecting FreeRTOS Objects in GDB

Basically, the FreeRTOS internal state is kind of hard to inspect 
when working with GDB. This project provides some scripts for GDB's 
Python API that make accessing some of these internals a little easier
to inspect. 

Requirements: 

1) You need to have the python API enabled in your version of GDB. This is a 
    compile time option when building GDB. You should be able to do something
	  like this: 

	gdb> python print "Hello World" 

	and get predictable results. If it throws an error - then you don't have 
	python compiled in your version of GDB.

2) Need to be using FreeRTOS 8.0+. This code could probably be used with FreeRTOS
    version 7.0 or previous versions, but the current code doesn't support it.

3) You need to use the Handle Registry for Queue info to be any use.
    Note that this only works for Queue based objects and not 
    for EventGroups 

This code adds the following custom GDB commands: 

- show List-Handle (symbol|address) [CastType]
	CastType is an optional argument that will cast all of the 
	handles in a list to a particular type. 
- show Task-List
- show Handle-Registry
- show Handle-Name  (symbole|address) 
- show Queue-Info [filter]
   filter can be "queue","mutex","semaphore", "counting", "recursive"



@TODO
=====

Currently, the EventGroup objects don't have an inspector. 
Work in progress - ideal solution would like modify the struct
of the Event Group to provide a similar piece of info that the 
Queue handle does so that we could use the same registry.
