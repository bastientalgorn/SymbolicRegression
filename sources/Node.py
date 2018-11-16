# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-

# Importation of the extern functions :
import random
import util
import numpy

#######################################
#                                     #
# definition of the structure of node #
#                                     #
#######################################

class Node():
    
    # ===========================
    #   Init
    # ===========================   

    def __init__(self, nodeType = None, value = None, nbArg = 0):
        self.__type = nodeType    # type of node (op, var or const)
        self.__nbArg = nbArg
        self.__h = None      # result of node     
        self.__logHMax = None 
        self.__error = None
        if self.__type == 'cte':
            self.__value = numpy.array(value) 
        else:
            self.__value = value

    # ===========================
    #   Copy
    # ===========================  

    def duplicate(self):
        # Create a new node
        newNode = Node(self.__type, self.__value, self.__nbArg)
        newNode.__error = self.__error
        newNode.__h     = self.__h
        newNode.__logHMax = self.__logHMax
        return newNode

    # ===========================
    #   Copy
    # ===========================  

    def __eq__(self,other):
        return self.__type==other.__type and self.__nbArg==other.__nbArg and self.__value==other.__value

    # ===========================
    #   Random constructor
    # ===========================  

    # Random constructor
    @classmethod
    def randomNode(cls, OpManager, varList):
        meanNbArg = OpManager.getMeanNbArg()
        EN = 5.0 # Expected number of nodes in this graph
        # We have:
        # EN = 1 + EN* ( 1*probaOpUnaire + 2*probaOpBinaire + 3*probaOpTernaire + ...)
        # If all operators have same probability
        # probaOpUnaire = probaOp * nbOpUnaire / nbOp
        # And same for probaBinaire, probaTernaire, etc.
        # We get:
        # EN = 1 + EN*ProbaOp ( 1*nbOpUnaire + 2*nbOpBinaire + 3*nbOpTernaire + ...)/nbOp
        # => EN = 1 + EN*ProbaOp*meanNbArg
        # => probaOp = (1 - 1/EN)/meanNbArg 
        probaOp = (1.0-1.0/EN)/meanNbArg 
        if random.random() < probaOp:
            # Creation of an operator node
            return Node.buildRandomOp( OpManager )
        else:
            # Creation of a leaf node
            return Node.buildRandomLeaf( varList )

    @classmethod
    def buildRandomLeaf(cls, varList):
        # Creation of a leaf node
        newNode = cls()
        newNode.__nbArg = 0 
        # TODO put this proba as a parameter
        if random.random() < 0.8:
            newNode.__type = "cte"
            newNode.__value = numpy.array(util.symmetricExp())
        else:
            newNode.__type = "var"
            newNode.__value = random.choice(varList)     
        return newNode

    @classmethod
    def buildRandomOp(cls, OpManager):
        # Create operator node
        newNode = cls()
        # Random draw of an operator
        op = OpManager.getRandomOp()
        # Set node's attributes
        newNode.__type = "op"
        newNode.__value = op[0]
        newNode.__nbArg = op[1]
        return newNode

    # ===========================
    # set, get & reset methods 
    # ===========================

    def reset(self, nodeType, value, nbArg = 0):
        self.__type = nodeType    # type of node (op, var or cte)
        self.__nbArg = nbArg
        if self.__type == 'cte':
            self.__value = numpy.array(value) 
        else:
            self.__value = value
        self.__h = None      # result of node
        self.__logHMax = None
        self.__error = None

    def setOp(self,op):
        if self.__type != 'op':
            print "Node.setOp : erreur de type"
        self.__value = op
        self.__h = None      # result of node
        self.__error = None

    def setVar(self,var):
        if self.__type != 'var':
            print "Node.setVar : erreur de type : node is of type "+self.__type
        self.__value = var
        self.__h = None      # result of node
        self.__error = None

    def setCte(self,cte):
        if self.__type != 'cte':
            print "Node.setCte : erreur de type"
        self.__value = numpy.array(cte)
        self.__h = None      # result of node
        self.__error = None

    def getType(self):
        return self.__type

    def getNbArg(self):
        return self.__nbArg

    def setNbArg(self,n):
        self.__nbArg = n

    def getValue(self):
        return self.__value

    def getString(self):
        if self.__type == "cte":
            return repr(float(self.__value))
        elif self.__type == "var":
            return "x"+str(self.__value)
        else:
            return self.__value

    def isLeaf(self):
        return self.__nbArg==0

    # About H ===============================

    def setH(self,v):
        self.__error = None
        self.__logHMax = None
        self.__h = v

    def getH(self):
        return self.__h
  
    def resetH(self):
        self.__h = None
        self.__logHMax = None
        self.__error = None

    def isHNone(self):
        return self.__h is None

    # About logHMax ===============================

    def setLogHMax(self,v):
        self.__logHMax = v

    def getLogHMax(self):
        return self.__logHMax

    def isLogHMaxNone(self):
        return self.__logHMax is None

    # About error ===============================

    def setError(self,v):
        self.__error = v

    def getError(self):
        return self.__error

    def isErrorNone(self):
        return self.__error is None


