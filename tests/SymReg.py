# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
# - build-in imports -
import sys
import os
import util


# Default values
inputDataFile = None
inputParamFile = "../inputs/MutationParameters_Full.txt"
inputDirName = "run_"+util.getDate()
inputRunNb = 1
inputGenNb = 10000
inputIndNb = 100

# Reading the inputs
if len(sys.argv) > 1:
    inputDataFile  = sys.argv[1]
    print "DataFile: "+inputDataFile
if len(sys.argv) > 2:
    inputParamFile = sys.argv[2]
    print "ParamFile: "+inputParamFile
if len(sys.argv) > 3:
    inputDirName  = sys.argv[3]
    print "DirName: "+inputDirName
if len(sys.argv) > 4:
    inputRunNb = int( sys.argv[4] )
    print "RunNb: "+str(inputRunNb)
if len(sys.argv) > 5:
    inputGenNb = int( sys.argv[5] )
    print "GenNb: "+str(inputGenNb)
if len(sys.argv) > 6:
    inputIndNb = int( sys.argv[6] )
    print "IndNb: "+str(inputIndNb)


# - PYGA imports -
from PYGA_GenAlg import PYGA_GenAlg

# - Local imports -
from RefModel import RefModel
from Individual import Individual
from GenAlgBehavior import MyGenAlgBehavior

# Definition of the list of enable operators
Individual.opListLoad('../inputs/operatorsList.txt')
# Chargement des paramètres de mutation
Individual.mutationParametersLoad(inputParamFile)
# Definition of the Reference Model
Individual.setRefModel(RefModel(inputDataFile))
# Error and Post-Processing
Individual.setErrorMethod("mse")
Individual.setPostProcessing("scalling")

outputList = 'tmp-progress end-pareto end-convergence'


for k in range(inputRunNb):
    # Set the seed
    util.setSeed()
    # Result directory definition
    resultDir = inputDirName+"_"+'{0:03}'.format(k+1)
    os.system("rm -rf "+resultDir+"/*")    
    MyGenAlgBehavior.setResultDir(resultDir)

    # Tmp Dir
    tmpDir = '/tmp/tmpSymReg/'+resultDir.split('/')[-1]
    os.system("rm -rf "+tmpDir+"/*")    
    MyGenAlgBehavior.setTmpDir(tmpDir)

    # Outputs definition
    MyGenAlgBehavior.setOutputList(outputList)

    # Copy of the main & seed files in the result directory
    os.system("cp seed.txt "+resultDir)

    # Create Genetic Algorithm with own individual and behavior
    genAlg = PYGA_GenAlg(Individual, MyGenAlgBehavior)

    # Set paramaters of the GA
    genAlg.setParameters(pop_size=inputIndNb,
                         nb_gen=inputGenNb,
                         crossrate=25,
                         mutaterate=40,
                         select='best',
                         cross_once=False,
                         reproduce_selected_only=False,
                         max_process=1,
                         del_duplicated_indiv=True
                         )

    # Run the GA...
    genAlg.run()
    print "Finished "+resultDir
    os.system("rm -rf "+tmpDir)    

