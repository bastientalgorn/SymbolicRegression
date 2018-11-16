# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
# - build-in imports -
import sys
import os
import util
from Graph import Graph

# - PYGA imports -
from PYGA_GenAlg import PYGA_GenAlg

# - Local imports -
from RefModel import RefModel
from Individual import Individual
from GenAlgBehavior import MyGenAlgBehavior

# Definition of operator list
Individual.opListLoad('../inputs/operatorsList.txt')
# Load mutation parameters
Individual.mutationParametersLoad("../inputs/MutationParameters_Choice.txt")
# Set Reference Model
Individual.setRefModel(RefModel("Quintic"))

g1=Graph.createRandomGraph()
g2=Graph.createRandomGraph()

coef = Graph.getLinearCrossoverCoef([g1,g2])
print coef

g3 = Graph.linearCrossover([g1,g2],coef)

