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

# Definition of the list of enable operators
Individual.opListLoad('../inputs/operatorsList.txt')
# Chargement des paramètres de mutation
Individual.mutationParametersLoad("../inputs/MutationParameters_Choice.txt")
# Definition of the Reference Model
Individual.setRefModel(RefModel("Quintic"))
# Error and Post-Processing
Individual.setErrorMethod("mse")
Individual.setPostProcessing("scalling")

for k in range(10):
    # Set the seed
    util.setSeed(k)
    # Definition of the result Directory
    resultDir = "result_"+__file__.replace(".py","")+"_"+util.getDate()
    MyGenAlgBehavior.setResultDir(resultDir)
    # Definition du niveau de blabla
    MyGenAlgBehavior.setVerboseLevel(3)
    # Copy of the main & seed files in the result directory
    os.system("cp "+__file__+" "+resultDir)
    os.system("cp seed.txt "+resultDir)

    # Create Genetic Algorithm with own individual and behavior
    genAlg = PYGA_GenAlg(Individual, MyGenAlgBehavior)

    # Set paramaters of the GA
    genAlg.setParameters(pop_size=30,
                         nb_gen=100,
                         crossrate=25,
                         mutaterate=40,
                         select='best',
                         cross_once=False,
                         reproduce_selected_only=False,
                         max_process=0,
                         del_duplicated_indiv=True
                         )

    # Run the GA...
    genAlg.run()

