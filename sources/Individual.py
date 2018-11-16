# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-

from PYGA_StandardMultiObjIndividual_NSGAII import PYGA_StandardMultiObjIndividual_NSGAII
import os
import random
import sys
import numpy
import util
from Graph import Graph


class Individual(PYGA_StandardMultiObjIndividual_NSGAII):

    NB_OBJECTIVES = 2
    __NB_NODES_LIMIT = 20
    __REF_MODEL = None
    __MUTATION_PARAMETERS = None


    @classmethod
    def setRefModel(cls, refModel):
        cls.__REF_MODEL = refModel
        Graph.setRefModel(refModel)

    @classmethod
    def setPostProcessing(cls, pp):
        Graph.setPostProcessing(pp)

    @classmethod
    def setErrorMethod(cls, oe):
        Graph.setErrorMethod(oe)

    @classmethod
    def opListLoad(cls, filename):
        Graph.opListLoad(filename)

    @classmethod
    def printOperatorList(cls):
        Graph.printOperatorList()

    @classmethod
    def setNbNodesLimit(cls, n):
        n = max(n,20)
        cls.__NB_NODES_LIMIT = n

    @classmethod
    def mutationParametersLoad(cls, filename):
        cls.__MUTATION_PARAMETERS = numpy.loadtxt(filename)
        print "Mutation Parameters: "+str(cls.__MUTATION_PARAMETERS)

    def __init__(self):
        PYGA_StandardMultiObjIndividual_NSGAII.__init__(self)
        self.__graph = None

    @classmethod
    def generate(cls,nbNodesLimit=20):
        # 1- Create the new individual
        newInd = cls()
        # 2- Generate the graph
        newInd.__graph = Graph.createRandomGraph(nbNodesLimit)
        # 3 - Return the generated individual...
        return newInd

    @classmethod
    def generateFromGraph(cls,graph):
        # 1- Create the new individual
        newInd = cls()
        # 2- Generate the graph
        newInd.__graph = graph.duplicate()
        # 3 - Return the generated individual...
        return newInd

    @classmethod
    def loadInd(cls,fileName):
        # 1- Create the new individual
        newInd = cls()
        # 2- Generate the graph
        newInd.__graph = Graph.loadGraph(fileName) 
        # 3 - Increase the __NB_NODES_LIMIT so that the graph is not cut
        nb = newInd.getNbNodes()
        if cls.__NB_NODES_LIMIT < nb:
            print "  NB_NODES_LIMIT <- "+str(nb)
            cls.setNbNodesLimit(nb)
        # 4 - Return the generated individual...
        return newInd

    def __str__(self):
        strObj = str(self.getObj()).replace('[', '').replace(']', '').replace(',',' ; ')
        return strObj

    def checkConsistency(self,position):
        self.__graph.checkConsistency(position)

    def objectives(self, population):
        obj1 = self.getError()
        obj2 = self.getComplexity()
        if numpy.isnan(obj1):
            obj1 = float('inf');
        if numpy.isnan(obj2):
            obj2 = float('inf');
        self.setObj([obj1 ,obj2])

    def getError(self):
        return self.__graph.getError()

    def getComplexity(self):
        return self.__graph.getComplexity()

    def getGraph(self):
        return self.__graph

    def getNbNodes(self):
        return self.__graph.getNbNodes()

    def getFullNbNodes(self):
        return self.__graph.getFullNbNodes()

    def getF(self):
        return self.__graph.getF()

    def getH(self):
        return self.__graph.getH()

    def getLogHMax(self):
        return self.__graph.getLogHMax()

    def printLinks(self):
        self.__graph.printLinks()


    # ==================================== #
    #       ERROR OBJECTIVE METHODS        #
    # ==================================== #

    # Maximum value of the error
    def getMaxError(self):
        return self.__graph.getMaxError()

    # MSE: Mean Square Error
    def getMeanSquareError(self):
        return self.__graph.getMeanSquareError()

    # Mse Check - Independant calculation of the mse.
    # Used for debug.
    def getMseCheck(self):
        return self.__graph.getMseCheck()

    # Max relative error (is 0 when fRef is 0)
    def getMaxRelativeError(self):
        return self.__graph.getMaxRelativeError()

    # Correlation error: 1 - correlation
    def getCorrelationError(self):
        return 1 - self.getCorrelation()




    # ==================================== #
    #          RESULT PROCESSING           #
    # ==================================== #

    def getError(self):
        return self.__graph.getError()

    def getRelativeError(self):
        return self.__graph.getRelativeError()

    def getDenormalizedResult(self):
        return self.__graph.getDenormalizedResult()

    def getAlgo(self):
        return self.__graph.getAlgo()

    def getCorrelation(self):
        return self.__graph.getCorrelation()

    def getString(self):
        return self.__graph.getString()

    def writePdfFile(self , fileName="Graph"):
        # Write dot file
        self.writeDotFile(fileName)
        # Compilation
        os.system("dot -Tpdf "+fileName+".dot -o "+fileName+".pdf &")

    def writeDotFile(self , fileName="Graph"):
        tab = self.__graph.getDot()
        fid = open(fileName+".dot", 'w')
        for e in tab:
            fid.write(e)
        fid.close()


    def writeIndFile(self , fileName="Graph" ):
        fid = open(fileName+'.ind', 'w')

		fid.write('# FileName\n'+fileName+'.ind\n\n')
		fid.write('# DataFile\n'+self.__REF_MODEL.getName()+'\n\n')
		fid.write('# VariablesNumber\n'+str(self.__graph.getNbVariables())+'\n\n')
		fid.write('# UsedVariables\n'+str(self.__graph.getListUsedVariables())+'\n\n')

        fid.write('# NodesNumber\n'+str(self.getNbNodes())+'\n\n')
        fid.write('# FullNodeNumber\n'+str(self.getFullNbNodes())+'\n\n')
        fid.write('# Complexity\n'+str(self.getComplexity())+'\n\n')        
        fid.write('# MeanSquareError\n'+str(self.getMeanSquareError())+'\n\n')        
        #fid.write('# CorrelationError\n'+str(1-self.getCorrelation())+'\n\n')
        fid.write('# MaxError\n'+str(self.getMaxError())+'\n\n')        
        fid.write('# MaxRelativeError\n'+str(self.getMaxRelativeError())+'\n\n')        
        fid.write('# Correlation\n'+str(self.getCorrelation())+'\n\n')     
        fid.write('# MseCheck\n'+str(self.getMseCheck())+'\n\n')   
        fid.write('# LogHMax\n'+str(self.getLogHMax())+'\n\n')   

        #fid.write('# String\n'+self.getString()+'\n\n')    

        #fid.write("# Algo\n");
        #for i in self.getAlgo():
        #    fid.write(i+"\n");            
        #fid.write("\n");

        fid.write("# Graph\n")
        tab = self.__graph.getStructureString()
        for e in tab:
            fid.write(e+"\n")
        fid.write("\n")


        fid.write("# Operators\n");
        for op in self.__graph.getOperatorsList():
            fid.write(op+"\n")
        fid.write("\n")


        fid.write("# Scalling\n");
        for v in self.__graph.getScallingValues():
            fid.write(str(v)+"\n")
        fid.write("\n")



        #fid.write('# F\n')
        #fid.write(str(self.getF()).replace('[',' ').replace(']',' '))
        #fid.write('\n\n')        

        #fid.write('# H\n')
        #fid.write(str(self.getH()).replace('[',' ').replace(']',' '))
        #fid.write('\n\n')    

        #fid.write('# Error\n')
        #fid.write(str(self.getError()).replace('[',' ').replace(']',' '))
        #fid.write('\n\n')    

        #fid.write('# Relative Error\n')
        #fid.write(str(self.getRelativeError()).replace('[',' ').replace(']',' '))
        #fid.write('\n\n')    

        fid.close() 
    
    def writeMatlabFile(self, fileName="Graph"):
        # Write the model
        fid = open(fileName+'.m', 'w')
		functionName = fileName
        if '/' in functionName:
            functionName = functionName.split("/")[-1]
        # First line
        fid.write('function f = '+functionName+'(varargin)\n\n')

		# Comments:
		fid.write('% FileName = '+fileName+'.m\n')

        if self.__REF_MODEL.getName() is not None:
    		fid.write('% DataFile = '+self.__REF_MODEL.getName()+'\n')
        if self.__REF_MODEL.getRefFunction() is not None:
    		fid.write('% MeanSquareError = '+str(self.getMeanSquareError())+'\n')
		fid.write('% NodesNumber = '+str(self.getNbNodes())+'\n')
		fid.write('% UsedVariables = '+str(self.__graph.getListUsedVariables())+'    ( '+str(self.__graph.getNbUsedVariables())+' out of '+str(self.__graph.getNbVariables())+' )\n')
		fid.write('\n')

        # Inputs management
        fid.write("%% Inputs Management\n");
        if self.__REF_MODEL.getNbVariables()==1:
            fid.write("x0 = varargin{1};\n");
        else:
            # Number of variables
            fid.write("NX = "+str(self.__REF_MODEL.getNbVariables())+";\n")
            fid.write("if nargin==1\n")
            fid.write("    if size(varargin{1},2)~=NX\n")
            fid.write("        error(['The input argument must have ' num2str(NX) ' columns.']);\n")
            fid.write("    end\n")
            fid.write("    for i=1:NX\n")
            fid.write("        eval(['x' num2str(i-1) ' = varargin{1}(:,' num2str(i) ');']);\n")
            fid.write("    end\n")
            fid.write("else\n")
            fid.write("    if nargin~=NX\n")
            fid.write("        error(['The function must have ' num2str(NX) ' arguments.']);\n")
            fid.write("    end\n")
            fid.write("    for i=1:NX\n")
            fid.write("        eval(['x' num2str(i-1) ' = varargin{' num2str(i) '};']);\n")
            fid.write("    end\n")
            fid.write("end\n")

        # Write the algorithm
        fid.write("\n%% Algorithm\n");
        for i in self.getAlgo():
            fid.write(i+";\n")     
        
        # Write the accessory functions
        fid.write("\n%% Accessory functions\n");
        fid.write("function z = mysqrt(x)\nz = sqrt(max(x,0));\n")
        fid.write("function z = powgen(x,y)\nz = (abs(x).^y).*cos(pi*y.*(x<0));\n")
        fid.write("function z = mymax(varargin)\nz = varargin{1};\nfor i=2:nargin\n    z = max(z,varargin{i});\nend\n")
        fid.write("function z = mymin(varargin)\nz = varargin{1};\nfor i=2:nargin\n    z = min(z,varargin{i});\nend\n")

        # Close
        fid.lose() 


    def __eq__(self, other):
        return (self.getObj() == other.getObj()) and (self.__graph == other.__graph)
        
    # ==================================== #
    #         CROSSOVER METHODES           #
    # ==================================== #
    @classmethod
    def crossover(cls, parent1, parent2):
        newInd = cls()
        newInd.__graph = Graph.externalCrossover(parent1.__graph,parent2.__graph)
        return newInd


    # ==================================== #
    #          MUTATION METHODES           #
    # ==================================== #
    @classmethod
    def mutation(cls, individual):
        # Copy of the individual
        newInd = cls()
        newInd.__graph = individual.__graph.duplicate()
        N = newInd.getNbNodes()
        tabProba = numpy.empty(9, 'float32')


        # OP 0: mutationInternCrossover (Ramification interne):
        #    Condition: At least 4 nodes
        tabProba[0] = cls.__MUTATION_PARAMETERS[0] * (N>=4)

        # OP 1: operator mutationLeaf2Leaf:
        #    Condition: None
        tabProba[1] = cls.__MUTATION_PARAMETERS[1] 

        # OP 2: operator mutationOp2Op
        #    Condition: At least 2 nodes
        tabProba[2] = cls.__MUTATION_PARAMETERS[2] * (N>=2)

        # OP 3: operator mutationLeaf2Op:
        #    Condition: None
        #    Favor on small graphs
        tabProba[3] = cls.__MUTATION_PARAMETERS[3] + cls.__MUTATION_PARAMETERS[4]*(N<=4)

        # OP 4: operator mutationOp2Leaf:
        #    Condition: At least 2 nodes
        tabProba[4] = cls.__MUTATION_PARAMETERS[5]*(N>=2) + cls.__MUTATION_PARAMETERS[6] * max(0,N-10) * max(1,N-50)

        # OP 5: operator mutationShortenGraph:
        #    Condition: At least 2 nodes
        tabProba[5] = cls.__MUTATION_PARAMETERS[7]*(N>=2) + cls.__MUTATION_PARAMETERS[8] * max(0,N-10) * max(1,N-50)

        # OP 6: operator mutationCreateLink:
        #    Condition: At least 6 nodes
        tabProba[6] = cls.__MUTATION_PARAMETERS[9]*(N>=6) + cls.__MUTATION_PARAMETERS[10] * max(0,N-10)

        # OP 7: operator mutationKeepBest:
        #    Condition: At least 2 nodes
        tabProba[7] = cls.__MUTATION_PARAMETERS[11]*(N>=2) 

        # OP 8: operator mutationConstants:
        #    Condition: At least 2 nodes
        tabProba[8] = cls.__MUTATION_PARAMETERS[12] *(N>=2) 

        # Normalize propa
        tabProba = tabProba.cumsum()
        tabProba /= tabProba[-1]
        # Pick mutation index
        r = random.random()
        iMut = numpy.count_nonzero(r>tabProba)

        # Call mutation
        newInd.__graph.callMutation(iMut)
        return newInd


    # ==================================== #
    #          MUTATION METHODES           #
    # ==================================== #
    def simplify(self):
        # Apply ShortenGraph and Keep Best operations to the node.
        self.__graph.callMutation(5)







