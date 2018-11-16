# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
import os
import inspect
import numpy
import util
import math
import glob
import time
from Graph import Graph
from Individual import Individual
from PYGA_StandardGenAlgBehavior import PYGA_StandardGenAlgBehavior

class MyGenAlgBehavior(PYGA_StandardGenAlgBehavior):

    __RESULT_DIR = "results"
    __TMP_DIR = "/tmp/SymReg"
    __VERBOSE_LEVEL = 2
    __OUTPUT_LIST = []
    __BEST = None
    __SIGMA_OBJ1 = 0
    __LOAD_DIRECTORIES = []
    __SUPER_INDIV_ERROR = float('inf')
    __GENERATION_STARTING_TIME = None
    __CONVERGENCE = []
    __LAST_PRINT_TIME = None

    @classmethod
    def setResultDir(cls,d):
        cls.__RESULT_DIR = d
        os.system('mkdir -p '+cls.__RESULT_DIR+' 2>/dev/null')
        #print "Output directory: "+cls.__RESULT_DIR

    @classmethod
    def setTmpDir(cls,d):
        cls.__TMP_DIR = d
        #print "Tmp directory: "+cls.__TMP_DIR

    @classmethod
    def resetStatistics(cls):
        cls.__BEST = None
        cls.__SIGMA_OBJ1 = 0

    @classmethod
    def setVerboseLevel(cls,d):
        print "***********************************************************************"
        print "Function \"setVerboseLevel\" is not supported anymore."
        print "Use function setOuputList"
        print "***********************************************************************"
        util.quit(__file__)


    @classmethod
    def setOutputList(cls,s):
        cls.__OUTPUT_LIST = s.split(' ')
        authorizedWords = [ 
            ['m','Write the \'.m\' file (Matlab file)'],
            ['pdf','Write the \'.pdf\' file (Graphic visualization of the Graph)'],
            ['dot','Write the \'.dot\' file (Source code for the pdf file)'],
            ['convergence','Write convergence file at each generation'],
            ['pareto-history','Write Pareto history'],
            ['current','Write current best individual at each generation'],
            ['duration','Write the duration of each generation'],
            ['progress','Write the progress of the optimization'],
            ['tmp-progress','Write the progress of the optimization in tmp directory'],
            ['super-ind','Compute a super-individual at each generation'],
            ['info-generation','Display the generation number'],
            ['info-improvement','Display all improvements'],
            ['info-operator','Display the operators list'],
            ['info-pygenalg','Display the pygenalg parameters'],
            ['end-convergence','(End of optimization) Write the convergence file'],
            ['end-pareto','(End of optimization) Write the complete pareto front'],
            ['end-node-call','(End of optimization) Write the number H calculations'],
            ['end-sigma','(End of optimization) Write sigma-obj1 in a file'],
            ['all','All the above-mentionned outputs']
        ]

        # Suppression of empty elements
        while "" in cls.__OUTPUT_LIST:
            cls.__OUTPUT_LIST.remove("")

        # Verification of validity of the keywords
        for w in cls.__OUTPUT_LIST:
            if not w in [x for (x,y) in authorizedWords]:
                print "***********************************************************************"
                print 'The word \"'+w+'\" is not authorized in outputList'
                print 'Authorized words:'
                lenMax = max([len(x) for (x,y) in authorizedWords])
                for w in authorizedWords:
                    s=w[0]+' '
                    while len(s)<lenMax+3:
                        s+='.'
                    s+=' '+w[1]
                    print '  '+s
                print "***********************************************************************"
                util.quit(__file__)

        # If "all", they use all authorized words
        if 'all' in cls.__OUTPUT_LIST:
            cls.__OUTPUT_LIST = [x for (x,y) in authorizedWords]

        # If "pdf", then remove "dot".
        if 'pdf' in cls.__OUTPUT_LIST and 'dot' in cls.__OUTPUT_LIST:
            # The writing of the pdf will, anyway, write the dot file
            cls.__OUTPUT_LIST.remove('dot')

        # If "convergence", then remove "end-convergence".
        if 'convergence' in cls.__OUTPUT_LIST and 'end-convergence' in cls.__OUTPUT_LIST:
            cls.__OUTPUT_LIST.remove('end-convergence')

        if 'tmp-progress' in cls.__OUTPUT_LIST:
            os.system('mkdir -p '+cls.__TMP_DIR+' 2>/dev/null') 



    @classmethod
    def loadDirectories(cls,dirName):
        addDir = glob.glob(dirName)
        for d in addDir:
            if os.path.isdir(d):
                cls.__LOAD_DIRECTORIES.append(d)    
                print "Directory to load: "+d

    @classmethod
    def getSigmaObj1(cls):
        print "SigmaObj1: "+str(MyGenAlgBehavior.__SIGMA_OBJ1)
        return MyGenAlgBehavior.__SIGMA_OBJ1

    def startOfRun(self):
        if 'info-operator' in self.__OUTPUT_LIST:
            Individual.printOperatorList()
        if 'info-pygenalg' in self.__OUTPUT_LIST:
            print '***********************************************************************'
            print 'PYGENALG parameters:'
            self.printInformation()

    def startOfLoop(self,population):
        # TODO: Check unicity of directories
        addGraph = []
        for d in MyGenAlgBehavior.__LOAD_DIRECTORIES:
            print "Loading directory: "+d
            s = "."+os.sep+d+os.sep+"*.ind"
            indFilesList = glob.glob(s)
            if not indFilesList:
                print "  Not .ind file in this directory"
            for indFile in indFilesList:
                try:
                    ind = Individual.loadInd(indFile)
                    population.addIndividual(ind)
                except:
                    print "  File not valid : "+indFile 



    def startOfGeneration(self, population, iGeneration):
        self.__GENERATION_STARTING_TIME = time.time()
        if 'info-generation' in self.__OUTPUT_LIST:
            print 'Generation '+str(1+iGeneration)+"/"+str(self.getParam(self.NB_GENERATIONS_LABEL))

    def endOfGeneration(self, population, iGeneration):

        #=================#
        #      CHECKS     #
        #=================#

        # Find new best individual
        popBestIndividual = population.getBestIndividual()
        newBestObj1 = float('inf')
        newBestObj2 = float('inf')
        for indiv in popBestIndividual:
            obj1 = indiv.getObj()[0]
            obj2 = indiv.getObj()[1]
            #print "bestPop : "+str(obj1)+" "+str(obj2)
            if (obj1<=newBestObj1) or (obj1==newBestObj1 and obj2<newBestObj2):
                newBestInd  = indiv
                newBestObj1 = obj1
                newBestObj2 = obj2

        # Get old best individual objectives
        if self.__BEST is None:
            oldBestObj1 = float('inf')
            oldBestObj2 = float('inf')
        else:
            oldBestObj1 = self.__BEST.getObj()[0]
            oldBestObj2 = self.__BEST.getObj()[1]

        # Check Regression
        if oldBestObj1<newBestObj1*(1-util.MACHINE_EPS):
            print "\n"
            print "Error : regression of the objectives !"
            print "old : "+str(oldBestObj1)+"  vs  new : "+str(newBestObj1)
            util.quit(__file__)



        #=================#
        #      INFOS      #
        #=================#

        # Calcul Sigma Obj1 
        self.__SIGMA_OBJ1 += newBestObj1 * iGeneration

        # Total number of generations
        nbGenMax = self.getParam(self.NB_GENERATIONS_LABEL)



        #=================#
        #     OUTPUTS     #
        #=================#

       
        # Check Improvement
        if (iGeneration==1) or (iGeneration==nbGenMax) or (oldBestObj1>newBestObj1) or (oldBestObj1==newBestObj1 and oldBestObj2>newBestObj2):

            # Memorization of the new best individual
            self.__BEST = newBestInd

            # Check the consistancy of the best Individual
            newBestInd.checkConsistency('GenAlgBehavior:endOfGeneration, newBestInd')

            # Update the maximum number of nodes in a graph
            Individual.setNbNodesLimit(3*newBestInd.getNbNodes())

            # Save best individual (duplicate and improve it before saving)
            if 'current' in self.__OUTPUT_LIST:            
                g = newBestInd.getGraph().duplicate()
                g.mutationKeepBest()
                g.mutationShortenGraph()
                newBestIndCopy = Individual.generateFromGraph(g)
                name = self.__RESULT_DIR+'/model_current'
                # Write the .ind file
                newBestIndCopy.writeIndFile(name)
                if 'dot' in self.__OUTPUT_LIST:
                    newBestIndCopy.writeDotFile(name)
                if 'pdf' in self.__OUTPUT_LIST:
                    newBestIndCopy.writePdfFile(name)
                if 'm' in self.__OUTPUT_LIST:
                    newBestIndCopy.writeMatlabFile(name)

            if 'info-improvement' in self.__OUTPUT_LIST:
                # Print last improvment
                print "Obj1: "+str(newBestObj1)+" Obj2: "+str(newBestObj2)

            if 'convergence' in self.__OUTPUT_LIST:
                # Write obj1 in statistic file
                fid = open(self.__RESULT_DIR+'/convergence.txt', 'a')
                fid.write(  str(iGeneration)+" "+str(newBestObj1)+" "+str(newBestObj2)+"\n" )
                fid.close()

            if 'end-convergence' in self.__OUTPUT_LIST:
                self.__CONVERGENCE.append([iGeneration, newBestObj1, newBestObj2])

        # Write Pareto history
        if 'pareto-history' in self.__OUTPUT_LIST:
            # For Q = 2, pareto front is written if
            # iGen is in [1 3 10 31 100 316 1000 3162 10000 31622 etc...]
            NR = numpy.power(10,numpy.floor(numpy.log10(iGeneration)))
            Q = 5
            tab = numpy.round(NR*pow(10,numpy.array(range(Q))/float(Q)))
            if (iGeneration in tab) or (iGeneration==nbGenMax):
                self.writeParetoObj(iGeneration,population)

        # Build super linear graph
        if 'super-ind' in self.__OUTPUT_LIST:
            graphList = []
            for indiv in popBestIndividual:
                g = indiv.getGraph()
                logHMax = g.getLogHMax()
                if not ( g.isConstant() or numpy.isinf(logHMax) or numpy.isnan(logHMax) ):
                    graphList.append(g)
            if len(graphList)>2:    
                gn=Graph.linearCrossover(graphList)
                if gn is not None:
                    superIndiv = Individual.generateFromGraph(gn)
                    superIndivError = superIndiv.getError()
                    if superIndivError < self.__SUPER_INDIV_ERROR and superIndivError < newBestObj1 : 
                        print " Obj1: "+str(superIndiv.getError())+" Obj2: "+str(superIndiv.getComplexity())+" (SuperInd)"
                        superIndiv.checkConsistency('GenAlgBehavior:endOfGeneration, superIndiv')
                        name = self.__RESULT_DIR+'/model_sup'
                        superIndiv.writeIndFile(name)
                        if 'dot' in self.__OUTPUT_LIST:
                            superIndiv.writeDotFile(name)
                        if 'pdf' in self.__OUTPUT_LIST:
                            superIndiv.writePdfFile(name)
                        if 'm' in self.__OUTPUT_LIST:
                            superIndiv.writeMatlabFile(name)

                        self.__SUPER_INDIV_ERROR = superIndivError


        if 'duration' in self.__OUTPUT_LIST:
            generationDuration = time.time() - self.__GENERATION_STARTING_TIME
            fid = open(self.__RESULT_DIR+'/duration.txt', 'a')
            fid.write(str(iGeneration)+" "+str(generationDuration)+"\n" )
            fid.close()    

        if 'progress' in self.__OUTPUT_LIST:
            fid = open(self.__RESULT_DIR+'/progress.txt', 'w')
            fid.write(str(iGeneration)+"/"+str(self.getParam(self.NB_GENERATIONS_LABEL))+" "+str(newBestObj1)+" "+str(newBestObj2))
            fid.close()    

        if 'tmp-progress' in self.__OUTPUT_LIST:
            if self.__LAST_PRINT_TIME is None or (time.time()-self.__LAST_PRINT_TIME>10):
                self.__LAST_PRINT_TIME = time.time()
                fid = open(self.__TMP_DIR+'/progress.txt', 'w')
                fid.write(str(iGeneration)+"/"+str(self.getParam(self.NB_GENERATIONS_LABEL))+" "+str(newBestObj1)+" "+str(newBestObj2))
                fid.close()    

    def endOfRun(self, population):

        # Store in a file the final pareto front
        popBestIndividual = population.getBestIndividual()
        # Get pareto indexes
        sortedIndex = self.getParetoIndexes(population)
        # Total number of generations
        nbGenMax = self.getParam(self.NB_GENERATIONS_LABEL)

        if 'end-pareto' in self.__OUTPUT_LIST:
            # Write the pdf graphs and result of the indiv from the pareto set
            k = 0
            lastObj2=None
            for index in sortedIndex:
                indiv = popBestIndividual[index]
                obj1 = indiv.getObj()[0]
                obj2 = indiv.getObj()[1]
                if not obj2==lastObj2:
                    # The individual number is written on 3 digits : 001, 002, 003, etc...
                    name = self.__RESULT_DIR+'/model_'+'{0:03}'.format(k+1)+'_'+str(obj1)+'_'+str(obj2)
                    indiv.writeIndFile(name)
                    if 'dot' in self.__OUTPUT_LIST:
                        indiv.writeDotFile(name)
                    if 'pdf' in self.__OUTPUT_LIST:
                        indiv.writePdfFile(name)
                    if 'm' in self.__OUTPUT_LIST:
                        indiv.writeMatlabFile(name)
                    k+=1
                    lastObj2=obj2


        if 'end-node-call' in self.__OUTPUT_LIST:
            # Writing the statistics
            fid = open(self.__RESULT_DIR+'/node-call.txt', 'a')
            fid.write('# NODE_RESULT_CALL\n'+str(Graph.getNodeHCall())+'\n')
            fid.write('# NODE_RESULT_CALCULATION\n'+str(Graph.getNodeHCalculation())+'\n')
            fid.close()

        if 'end-sigma' in self.__OUTPUT_LIST:
            fid = open(self.__RESULT_DIR+'/sigma.txt', 'w')
            fid.write(str(self.__SIGMA_OBJ1))
            fid.close()

        if 'end-convergence' in self.__OUTPUT_LIST:
            fid = open(self.__RESULT_DIR+'/convergence.txt', 'w')
            for e in self.__CONVERGENCE:
                s = str(e[0])
                while len(s)<numpy.log10(nbGenMax)+2:
                    s+=' '
                fid.write(s+str(e[1])+" "+str(e[2])+'\n')
            fid.close()


        return False



    # Overload crossover
    # Do not cross individual with only one node
    def crossover(self, population, nbCrossInd, newPop):
        # 1- Create the new population
        # -- It will contain only all individuals generated by crossover
        crossedPopulation = self.createPopulation()
        # 2- Generate enought individuals
        while crossedPopulation.size() < nbCrossInd:
            # 2.1- Get the parents to cross
            crossOnce = self.getParam(self.CROSS_ONCE_LABEL)
            # 2.2- Call cross method from individual class
            duplicated = True
            while duplicated:
                parents = population.getRandomParents(useTwice=(not crossOnce))
                count = 0
                while (1 in [parents[0].getComplexity(), parents[1].getComplexity()]) and (count<200):
                    parents = population.getRandomParents(useTwice=(not crossOnce))
                    count += 1


                newIndiv = self.individualCrossover(parents[0], parents[1])
                duplicated = False
                if self.getParam(self.DEL_DUPLICATED_INDIV_LABEL):
                    for indiv in newPop:
                        if newIndiv.isDuplication(indiv):
                            duplicated = True
                            break
                    if not duplicated:
                        for indiv in crossedPopulation:
                            if newIndiv.isDuplication(indiv):
                                duplicated = True
                                break
            crossedPopulation.addIndividual(newIndiv)
        return crossedPopulation




    def bestSelection(self, population, nbIndSelected):
        # Verif on nbIndSelected:
        if nbIndSelected == 0:
            print "I don't understand how nbIndSelected could be null ?!!"
            exit()

        # 1 - FIND THE BEST INDIVIDUAL
        bestError =  float('inf')
        bestComplexity =  float('inf')
        for individual in population:
            bool1 = individual.getError() < bestError
            bool2 = individual.getError() == bestError and individual.getComplexity() < bestComplexity
            if bool1 or bool2:
                bestIndividual = individual
                bestError = individual.getError()
                bestComplexity = individual.getComplexity()
        #print "The bestIndividual has objectives : "+str(bestIndividual.getError())+" "+str(bestIndividual.getComplexity()) 


        # 2 - BUILD A PRELIMINARY POPULATION WHICH EXCLUDES:
        # - Individuals with only one node
        # - Individuals with nbNodes > 3* bestIndividual.nbNodes
        # - The best individual
        nbNodesLimit = 3*bestIndividual.getNbNodes()
        preliminaryPop = self.createPopulation()
        for individual in population:
            n = individual.getNbNodes()
            bool1 = n > 1
            bool2 = n < nbNodesLimit
            bool3 = individual is not bestIndividual
            if bool1 and bool2 and bool3:
                preliminaryPop.addIndividual(individual)

        # 3 - Build the population
        if preliminaryPop.size() >= nbIndSelected-1:
            # 3a - If the preliminary population is big enough, we use it to generate bestPop
            # (nb : we remove 1 because the best Individual will be added in the end)
            
            # Create the new population
            bestPop = self.createPopulation()
            for individual in preliminaryPop:
                if bestPop.size() < nbIndSelected-1:
                    bestPop.addIndividual(individual)
                else:
                    worstInd = None
                    for ind in bestPop:
                        if worstInd is None or self.isIndividualBetter(worstInd,ind,preliminaryPop):
                            worstInd = ind
                    if self.isIndividualBetter(individual, worstInd, preliminaryPop):
                        bestPop.removeIndividual(worstInd)
                        bestPop.addIndividual(individual)

        else:
            # 3b - If the preliminary population is not big enough, we use it as a starting point and we add 
            # Some of the points that have been rejected. 
            print "in bestSelection"
            print "nbIndSelected = "+str(nbIndSelected)
            print "preliminaryPop.size = "+str(preliminaryPop.size())
            print "NOT Big enough !"
            bestPop = preliminaryPop
            nbNodesTarget = bestIndividual.getNbNodes()
            if nbNodesTarget<5:
                nbNodesTarget=5
            while bestPop.size() < nbIndSelected-1:
                individual = Individual.generate(bestIndividual.getNbNodes())
                individual.objectives(population)
                bestPop.addIndividual(individual)

        # 4 - FINALLY, WE HAD THE BEST INDIVIDUAL
        bestPop.addIndividual(bestIndividual)

        return bestPop



    def getParetoIndexes(self,population):
        # Get pareto population
        popBestIndividual = population.getBestIndividual()
        # Order in regard of obj1
        objList = []
        for indiv in popBestIndividual:
            objList.append(indiv.getObj()[0])
        sortedIndex = sorted(range(len(objList)), key=objList.__getitem__)
        return sortedIndex


    def getParetoObj(self,population):
        # Get pareto population
        popBestIndividual = population.getBestIndividual()
        # Get pareto indexes
        sortedIndex = self.getParetoIndexes(population)

        # Build the tab with the objectives
        tab = []
        for index in sortedIndex:
            indiv = popBestIndividual[index]
            obj = indiv.getObj()
            if obj not in tab:
                tab.append(obj)
        return tab

    def writeParetoObj(self,iGeneration,population):
        # Get the ordered values of the objective of the point of the pareto front
        tab = self.getParetoObj(population)
        # Write them
        fid = open(self.__RESULT_DIR+'/pareto_history.txt', 'a')
        fid.write('# generation '+str(iGeneration)+'\n')
        for e in tab:
            fid.write(str(e[0])+' '+str(e[1])+'\n')
        fid.write('\n')
        fid.close()

