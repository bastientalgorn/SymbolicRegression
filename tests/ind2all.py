# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
# - build-in imports -
import sys
import os
import util

# - PYGA imports -
from PYGA_GenAlg import PYGA_GenAlg

# - Local imports -
from RefModel import RefModel
from Individual import Individual
from GenAlgBehavior import MyGenAlgBehavior

print "=========ind2all=================="

indFile = sys.argv[1]
if len(sys.argv) > 2:
    outFile = sys.argv[2]
    print "output name: "+outFile
else:
    outFile = indFile.replace('.ind','')

# Build a dummy RefModel
M = RefModel(None)

# Get the Nb of variables from the ind file
fid = open(indFile)
lines = fid.readlines()
fid.close()
lines = util.cleanLines(lines)
nbVariables = int(util.getField(lines,"VariablesNumber")[0])
dataFile = util.getField(lines,"DataFile")[0]
mse = float(util.getField(lines,"MeanSquareError")[0])


print "nbVariables: "+str(nbVariables)

Individual.setRefModel(M)
M.setNbVariables(nbVariables)
M.setName(dataFile)

Individual.opListLoad(indFile)
Ind = Individual.loadInd(indFile)


Ind.writeDotFile(outFile)
Ind.writeMatlabFile(outFile)


print "===========end===================="
