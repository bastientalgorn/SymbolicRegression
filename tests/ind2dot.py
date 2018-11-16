# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
# - build-in imports -
import util
import sys
from Individual import Individual


if len(sys.argv) > 1:
    indFileName  = sys.argv[1]
if len(sys.argv) > 2:
    dotFileName  = sys.argv[2]
else:
    dotFileName = indFileName.replace(".py","")

ind = Individual.generateFromFile(indFileName)


ind.writeDotFile(dotFileName)
