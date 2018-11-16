# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
# - build-in imports -
import sys
import os

# - PYGA imports -
from PYGA_GenAlg import PYGA_GenAlg

# - Local imports -
from RefModel import RefModel
from Node import Node
from Tree import Tree
from Individual import Individual
from GenAlgBehavior import MyGenAlgBehavior

INPUT_DIR = '../inputs'
# Definition of the list of enable operators
Node.opListLoad(os.path.join(INPUT_DIR, 'ListeOperateur.txt'))
# Definition of the Ref Model
MODELE_FUNCTION_NAME = 'x^2 (Reference)'
MODELE_FILE = os.path.join(INPUT_DIR, 'Modele_x2.txt')
M = RefModel(MODELE_FILE)
Node.setRefModel(M)
VARNUMBER = M.getNbVariables()+1

RESULT_DIR = 'results'
OBJECTIVES_FILE = os.path.join(RESULT_DIR, 'objectives.png')
RESULTS_FILE = os.path.join(RESULT_DIR, 'results.png')
PYGA_RES_FILE = os.path.join(RESULT_DIR, 'pyga.res')
PYGA_PARETO_FILE = os.path.join(RESULT_DIR, 'pyga_pareto.res')
PLOT_FILE = os.path.join(RESULT_DIR, 'res.plot')

os.system('rm -rf ' + RESULT_DIR)
os.system('mkdir ' + RESULT_DIR)



MyGenAlgBehavior.INDIV_GET_METHOD = ['getError', 'getComplexity']
MyGenAlgBehavior.INDIV_METH_VALUE = [0.0, 3]
MyGenAlgBehavior.INDIV_METH_CMP = ['==', '<=']



# Create Genetic Algorithm with own individual definition
genAlg = PYGA_GenAlg(Individual, MyGenAlgBehavior)

# Set paramaters of the GA
genAlg.setParameters(pop_size=50,
                     nb_gen=200,
                     crossrate=15,
                     mutaterate=25,
                     select='best',
                     cross_once=True,
                     exec_time=0,
                     reproduce_selected_only=False,
                     max_process=0,
                     del_duplicated_indiv=True
                     )

# Run it...
genAlg.run()

# Get the informations at the end of process
fid = open(PYGA_RES_FILE, 'w')
fid.write(str(genAlg.getPopulation()).replace('[', '').replace(']', ''))
fid.close()

# Get the informations at the end of process
fid = open(PYGA_PARETO_FILE, 'w')
paretoFront = genAlg.getPopulation().getBestIndividual()
s = ''
for indiv in paretoFront:
    s += str(indiv) + "    , "+indiv.getTextString() +'\n'
fid.write(s.replace('[', '').replace(']', ''))
fid.close()

fid = open('template.plot', 'r')
plot_lines = fid.readlines()
fid.close()

fid = open(PLOT_FILE, 'w')
for line in plot_lines:
    while '@' in line:
        startLine = line[:line.index('@')]
        subLine = line[line.index('@')+1:]
        var = subLine[:subLine.index('@')]
        endLine = subLine[subLine.index('@')+1:]
        line = startLine + str(eval(var)) + endLine
    if line.strip() != '':
        fid.write(line)

# Add individual lines
for i, indiv in enumerate(paretoFront):
    result = indiv.getResult()
    formula = indiv.getTextString()
    print str(indiv) + ' ' + formula
    filename = os.path.join(RESULT_DIR, 'res_indiv_'+str(i))
    fidindiv = open(filename, 'w')
    fidindiv.write('# Formula=' + formula + '\n')
    for ivar, res in enumerate(result):
        fidindiv.write(str(M.getVariable(0)[ivar]) + ' ' + str(res) + '\n')
    fidindiv.close()
    fid.write('     "'+filename+'" using 1:2 with points title "' + formula + '"')
    if i < len(paretoFront)-1:
        fid.write(',\\')
    fid.write('\n')
fid.close()
    

os.system('gnuplot ' + PLOT_FILE)
#os.system('display ' + OBJECTIVES_FILE)
os.system('display ' + RESULTS_FILE)
