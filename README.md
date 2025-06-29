# lpcs
LPC Savefile reader for python

This is a simple save file read (and writer) for lpc savefiles (in the `#3:2` flavour)

The savefile is bing transformed into a dictionery mapping the variables names to the contained values,
where ints, floats transformed into their Python equivalent, string escapes will only partially be resolved.
Arrays are transformed into lists and mappings are transformed into dicts mapping from string to a list
(as LPC mappings may contain more than one value).

The writer is intended to transform these data structures back into tair original form. However,
refs, being duplicated when read, will be written as multiple copies.

There is probaby a lot left to do:

* data structures I have overseen
* edge case with number representation
* proper string escaping and unescaping

