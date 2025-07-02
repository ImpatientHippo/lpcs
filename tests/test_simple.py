#!/usr/bin/env python3

import sys
sys.path.insert(1, './src')

import lpcs

savefile = "simple.o" if len(sys.argv)<2 else sys.argv[1]

with open(savefile,"r") as f:
  data = f.read()

sf = lpcs.lpc_loads(data)
assert sf["name"] == "simple"
assert sf["some_struct"][1] == 13
assert sf["newlines"] == "test\ntest\"and\\must be quoted"
assert len(sf["some_lwo"]) == 1
assert sf["fraction"] == 2.2
assert sf["number"] == 123

assert sf["some_ref"][0] == "test"
assert sf["some_ref"][1].deref() == "test"

#print( lpcs.lpc_dumps(sf) )
