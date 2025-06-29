#!/usr/bin/env python3

import sys
sys.path.insert(1, '.')

import lpcs

savefile = "simple.o" if len(sys.argv)<2 else sys.argv[1]

with open(savefile,"r") as f:
  data = f.read()

sf = lpcs.lpc_loads(data)
print( sf["name"] )
print( lpcs.lpc_dumps(sf) )
