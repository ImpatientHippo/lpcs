# lpcs
LPC savefile reader for python

This is a simple save file reader (and writer) for lpc savefiles (in the `#3:2` flavour)

The savefile is bing transformed into a dictionary, mapping the variables names to the contained values.
ints, floats are transformed into their Python equivalent, string escapes will only partially be resolved.
Arrays are transformed into lists and mappings are transformed into dicts mapping from string to a list
(as LPC mappings may contain more than one value).

The writer is intended to transform these data structures back into their original form.
However, refs, being duplicated when read, will be written as multiple copies.

There is probaby a lot left to do:

* data structures I may have overlooked
* edge case with number representation
* proper string escaping and unescaping
* other flavors?

# Basic Usage:

```
data = lpcs.lpc_load( "filename.o" )
# do sth with data
lpcs.lpc_dump( "filename.o", data )
print( lpcs.lpc_dumps(data) )
```
