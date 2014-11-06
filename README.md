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

This code adds the following custom GDB commands: 

- show FRList (symbol|address) [CastType]
- show Task-List
- show Handle-Registry
- show Handle-Name   