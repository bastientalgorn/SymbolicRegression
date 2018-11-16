# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-

# Importation of the extern functions :
import os
import math
import numpy
import random 
import sys

# biggest possible value in this machine
MACHINE_MAX_VALUE = numpy.finfo(numpy.float32).max
# log of this value
MACHINE_MAX_LOG = numpy.log(numpy.finfo(numpy.float32).max)
# machine precision
MACHINE_EPS = numpy.finfo(numpy.float32).eps
# On ignore les divisions par 0, les overflow et les underflow
numpy.seterr(all='ignore')

#sys.setrecursionlimit(50)

#######################################
# ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' #
# definition of the structure of node #
# ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' #
#######################################

class Node():
    
    # =============================================
    # classmethod relative to the reference model
    # =============================================
    @classmethod
    def setRefModel(cls,M):
        print "Definition du modele de reference pour la classe Tree"
        cls.refModel = M

    @classmethod
    def getVariable(cls,i):
        return cls.refModel.getVariable(i)

    @classmethod
    def getRandomVariableIndex(cls):
         return random.randint(0, Node.refModel.getNbVariables() - 1)


    @classmethod
    def symetricExp(cls):
        expParameter = 3
        x = random.expovariate(expParameter)
        p = random.random()
        if p > 0.5:
            return x
        else:
            return -x



    # =============================================
    # classmethod relative to the operator list
    # =============================================

    # class variable : 
    __bnOp = []    # list of the binary operators
    __unOp = []    # list of the unary operators
    __allOp = []    # list of all operators

    @classmethod
    def opListLoad(cls,fileName):
        print "Loading of the set of operators in the file : "
        print "   "+fileName
        fileId = open(fileName)
        lines = fileId.readlines()
        mat = []
        for line in lines:
            values = line.split(',')
            values[-1] = values[-1][0:-1]
            mat.append(values)
        # Filling the list of the operators:
        for i in range(0,len(mat)):
            if mat[i][1] == "bn":
                if mat[i][2] == "on":
                    cls.__bnOp.append(mat[i][0])
            if mat[i][1] == "un":
                if mat[i][2] == "on":
                    cls.__unOp.append(mat[i][0])
        cls.__allOp = cls.__unOp + cls.__bnOp
        print "   Unary Operator List : "+str(cls.__unOp)
        print "   Binary Operator List : "+str(cls.__bnOp)

    @classmethod
    def getBnOp(cls):
        return cls.__bnOp

    @classmethod
    def getUnOp(cls):
        return cls.__unOp

    @classmethod
    def getAllOp(cls):
        return cls.__allOp

    def printNode(self, printVal = True):
        if printVal:
            print self.__value
        if self.__left:
            print self.__left.__value, 
        else:
            print 'XL', 
        if self.__right:
            print self.__right.__value
        else:
            print 'XR',
        if self.__left:
            self.__left.printNode(False),
        if self.__right:
            self.__right.printNode(False)



    # ===========================
    #   NODE Methods
    # ===========================   
    def __init__( self, nodetype = None, value = None, left = None, right = None, result = None, level = 0):
        self.__value = value   # value of node
        self.__type = nodetype # type of node (binary, unary, variable or constant)
        self.__left = left     # left sun of node
        self.__right = right   # right sun of node
        self.__result = result # result of node     
        self.__level = level   # level du Node
        self.__correlation = None
        self.__id = None
        self.__fathers = []
        self.__fathersId = []
        self.__x = None        # the abscissa of the node

    def reset(self, nodetype = None, value = None, left = None, right = None, result = None, level = 0):
        # TODO: delete children to avoid memory leak?
        self.__value = value   # value of node
        self.__type = nodetype # type of node (binary, unary, variable or constant)
        self.__left = left     # left sun on node
        self.__right = right   # right sun of node
        self.__result = result # result of node     
        self.__level = level   # level du Node
        self.__correlation = None
        self.__id = None
        self.__x = None        # the abscissa of the node



    def getId(self):
        return self.__id

    def setId(self, newId):
        self.__id = newId

    def getValue(self):
        return self.__value

    def setValue(self, newVal):
        self.__value = newVal



    def setRandomLeaf(self):
        self.__right = None
        self.__left = None
        self.__result = None
        self.__level = None
        self.__correlation = None
        self.__id = None
        self.__x = None  
        if random.random() < 0.5:
            self.__type = 'cte'
            self.__value = Node.symetricExp()
        else:
            self.__type = 'var'
            self.__value = Node.getRandomVariableIndex()


    def resetResult(self):
        self.__result = None
        # On remet aussi la correlation a None
        self.__correlation = None

    def isResultNone(self):
        return (self.__result is None)




    def getType(self):
        return self.__type
    def setType(self, newType):
        self.__type = newType

    def getLevel(self):
        return self.__level

    def getLeftNode(self):
        return self.__left
    def setLeftNode(self, node):
        self.__left = node

    def getRightNode(self):
        return self.__right
    def setRightNode(self, node):
        self.__right = node




    def getFathers(self):
        return self.__fathers
        
    def setFathers(self, fathers):
        if fathers is None:
            self.__fathers = []
        else:
            self.__fathers = fathers

    def addFather(self, newFather):
        self.__fathers.append(newFather)

    def getFathersId(self):
        return self.__fathersId

    def setFathersId(self, newFathersId):
        self.__fathersId = newFathersId

    def addFatherId(self, newFatherId):
        self.__fathersId.append(newFatherId)





    def getAllLeafs(self):
        leafs = []
        if self.isLeaf():
            leafs.append(self)
        else:
            leafs += self.__left.getAllLeafs()
            if self.__right:
                leafs += self.__right.getAllLeafs()
        return leafs

    def getAllNodes(self):
        nodes = [self]
        if self.__left:
            nodes += self.__left.getAllNodes()
        if self.__right:
            nodes += self.__right.getAllNodes()
        return nodes

    def getDepth(self):
        dl = 0
        dr = 0
        if self.__left:
            dl = self.__left.getDepth()
        if self.__right:
            dr = self.__right.getDepth()
        depth = max(dl, dr) + 1
        return depth

    def __hash__(self):
        return self.__id
    
    def __eq__(self, other):
        boolean = False
        if (self.__type == other.__type) and (self.__value == other.__value):
            # If types and values are the same...
            if (self.__type == 'bn') and (self.__value in ['*', '+']):
                # If the operator is binary and symetric, then the equality has to
                # to be tested with crossed arguments
                boolean1 = self.__left == other.__left and\
                           self.__right == other.__right
                boolean2 = self.__right == other.__left and\
                           self.__left == other.__right
                boolean = boolean1 or boolean2
            else:
                boolean = (self.__left == other.__left) and\
                          (self.__right == other.__right)
        return boolean



    # ::::::::::::::::::::: #
    #        DUPLICATE      #
    # ::::::::::::::::::::: #
    def duplicate(self, fathers = None, duplicatedNodes = None):

        if self.__type == 'link':
            # Create a new node
            newNode = Node(self.__type,
                           None, # Value is None (it will be set later)
                           None,
                           None,
                           self.__result,
                           self.__level)
        else:
            # Create a new node
            newNode = Node(self.__type,
                           self.__value,
                           None,
                           None,
                           self.__result,
                           self.__level)



        # Manage father
        if fathers is None:
            newNode.__fathers = []
            newNode.__fathersId = []
        else:
            newNode.__fathers = fathers
            newNode.fathersId = []
            for father in fathers:
                newNode.__fathersId.append(father.__id)
            if len(fathers) > 1:
                if duplicatedNodes is None:
                    duplicatedNodes = [[],[]]
                duplicatedNodes[0].append(self)
                duplicatedNodes[1].append(newNode)

        # Set fixed variables
        newNode.__correlation = self.__correlation
        newNode.__id = self.__id
        newNode.__x = self.__x

        # Manage level
        nblvll = 0
        nblvlr = 0
        nbLevels = 1
        # Manage Leafs
        nbLeafs = 0
        # Manage nodes list
        nodesList = [newNode]

        # Duplicate left node
        if self.__left:
            duplicated = False
            if duplicatedNodes is not None:
                if self.__left in duplicatedNodes[0]:
                    index = duplicatedNodes[0].index(self.__left)
                    newNode.setLeftNode(duplicatedNodes[1][index])
                    duplicated = True
                    nbl = len(newNode.__left.getAllLeafs())
                    nblvll = newNode.__left.getDepth()
            if not duplicated:
                newNode.__left , nl, nbl, nblvll = self.__left.duplicate([newNode], duplicatedNodes)
                nodesList += nl
            nbLeafs += nbl
        else:
            # No left node -> leaf
            nbLeafs += 1

        # Duplicate right node
        if self.__right:
            duplicated = False ## NB : j'ai aussi rajouté cette ligne, comme pour "Duplicate Left". J'ai raison ???
            if duplicatedNodes is not None:
                if self.__right in duplicatedNodes[0]: ## NB : avant il y avait "left". Erreur ??
                    index = duplicatedNodes[0].index(self.__right)
                    newNode.setRightNode(duplicatedNodes[1][index])
                    duplicated = True
                    nbl = len(newNode.__right.getAllLeafs())
                    nblvlr = newNode.__right.getDepth()
            if not duplicated:
                newNode.__right , nl, nbl, nblvlr = self.__right.duplicate([newNode], duplicatedNodes)
                nodesList += nl
            nbLeafs += nbl
            
        # If type is Link, then duplicate the Value, using the same method as for left and right
        if self.__type == 'link':
            duplicated = False
            if duplicatedNodes is not None:
                if self.__value in duplicatedNodes[0]:
                    index = duplicatedNodes[0].index(self.__value)
                    newNode.__value(duplicatedNodes[1][index])
                    duplicated = True
                    # A link Node has one Leaf (itself) and its depth is 1
                    nbl = 1
                    nblvlr = 1 # Le nombre de Leaf 
            if not duplicated:
                newNode.__value , nl, nbl, nblvlr = self.__value.duplicate([newNode], duplicatedNodes)
                nodesList += nl
            nbLeafs += nbl


        # Get new level if changed
        nbLevels += max(nblvll, nblvlr)
   
        return newNode, nodesList, nbLeafs, nbLevels
                

    # @function      IsLeaf(): tests if a node is a leaf or no
    # @return        0 if a node is a leaf, 1 otherwhise
    def isLeaf(self):
        return (self.__left is None)


    # @function      isAncestor()
    def isAncestor(self,daddy):
        # true if daddy is one of the ancestor of self
        #print "Is N"+str(daddy.getId())+" an ancestor of N"+str(self.getId())+" ??"
        currentLevel = [self]
        boolean = False
        while (not boolean) and len(currentLevel):
            upperLevel = list()
            for n in currentLevel:
                #print str(n.id) + " vs " + str(daddy.id)
                if n.getId() == daddy.getId():
                    boolean = True
                    #print "     This is my daddy !"
                else:
                    #print "     N" + str(n.getId()) + " has "+str(len(n.getFathers()))+" father(s) : ",
                    for p in n.getFathers():
                        if p not in upperLevel:
                            upperLevel.append(p)
                            #print "N"+str(p.getId())+" ",
            print
            currentLevel = set(upperLevel)
        #if not boolean:print "     I'm NOT your father Luke !"
        return boolean


    # @function      recursiveRandomNode():
    def recursiveRandomNode(self, level):
        nbCreatedNodes = 0
        nodesList = [self]
        nbLeaf = 0
        nbLevels = 1
        while nbCreatedNodes == 0:
            if random.random()/max(level,1) > 0.2:
                # Creation d'un operateur
                if random.random() > 0.3 and len(Node.getBnOp()) > 0:
                    # Creation d'un operateur binaire
                    self.__type = "bn"
                    self.__value = random.choice(Node.getBnOp())
                    self.__left = Node()
                    self.__left.addFather(self)
                    nbNodes1, nodes1, nbLeaf1, nbLevels1 = self.__left.recursiveRandomNode(level+1)
                    self.__right = Node()
                    self.__right.addFather(self)
                    nbNodes2, nodes2, nbLeaf2, nbLevels2 = self.__right.recursiveRandomNode(level+1)
                    nbCreatedNodes += 1 + nbNodes1 + nbNodes2
                    nodesList += nodes1 + nodes2
                    nbLeaf += nbLeaf1 + nbLeaf2
                    nbLevels += max(nbLevels1, nbLevels2)
                    created = True
                elif len(Node.getUnOp()) > 0:
                    # Creation d'un operateur unaire
                    self.__type = "un"
                    self.__value = random.choice(Node.getUnOp())
                    self.__left = Node()
                    self.__left.addFather(self)
                    nbNodes, nodes, nbLeaf1, nbLevels1 = self.__left.recursiveRandomNode(level+1)
                    nodesList += nodes
                    nbCreatedNodes += 1 + nbNodes
                    nbLeaf += nbLeaf1
                    nbLevels += nbLevels1
                    created = True
            else:
                # creation d'une feuille
                if random.random() > 0.7:
                    self.__type = "cte"
                    self.__value = Node.symetricExp()
                else:
                    self.__type = "var"
                    self.__value = Node.getRandomVariableIndex()
                nbCreatedNodes += 1
                nbLeaf += 1
                created = True
        return nbCreatedNodes, nodesList, nbLeaf, nbLevels

    ##############################
    # EVALUTION OF TREE or NODES #
    ##############################

    def isResultNone(self):
        return self.__result is None


    def getResult(self):
        if self.__result is None:
            # if node is a unary operator 
            if self.__type == "bn":
                #print "getResult ========> bn"+str(self.__value)+" "+str(self.__left)+" "+str(self.__right)
                if self.__value == "+":
                    self.__result = self.__left.getResult() + self.__right.getResult()
                elif self.__value == "-":
                    self.__result = self.__left.getResult() - self.__right.getResult()
                elif self.__value == "*":
                    self.__result = self.__left.getResult() * self.__right.getResult()
                elif self.__value == "/":
                    self.__result = self.__left.getResult() / self.__right.getResult()
                elif self.__value == "^":
                    self.__result = numpy.sign(self.__left.getResult()) * pow(abs(self.__left.getResult()), self.__right.getResult())
                elif self.__value == "max":
                    self.__result = numpy.max(self.__left.getResult(), 
                                              self.__right.getResult())
                elif self.__value == "min":
                    self.__result = numpy.min(self.__left.getResult(), 
                                              self.__right.getResult())
            
            # if node is a unary operator
            elif self.__type == "un":
                #print "getResult ========> un"+str(self.__value)
                if self.__value == "sqrt":
                    self.__result = numpy.sign(self.__left.getResult()) * numpy.sqrt(abs(self.__left.getResult()))
                elif self.__value == "exp":
                    self.__result = numpy.exp(self.__left.getResult())
                elif self.__value == "ln":
                    self.__result = numpy.sign(self.__left.getResult()) * numpy.log(abs(self.__left.getResult()))
                elif self.__value == "sin":
                    self.__result = numpy.cos(self.__left.getResult())
                elif self.__value == "cos":
                    self.__result = numpy.cos(self.__left.getResult())
                elif self.__value == "tan":
                    self.__result = numpy.tan(self.__left.getResult())
                elif self.__value == "abs":
                    self.__result = abs(self.__left.getResult())
            # if node is a variable   
            elif self.__type == "var":
                #print "getResult ========> var"+str(self.__value)+" "+str(numpy.mean(Node.getVariable(self.__value)))
                self.__result = Node.getVariable(self.__value)
            # if node is a constant
            elif self.__type == "cte":
                #print "getResult ========> cte"+str(self.__value)
                self.__result = numpy.array([self.__value]*Node.refModel.getNbPoints())

            elif self.__type == "link":
                #print "getResult ========> link"+str(self.__value)
                self.__result = self.__value.getResult()

            else:
                print self.__type
                print "Et que de suie une errante prison\n\
                Eteinge dans l'horreur de ses noires trainées\n\
                Le soleil se mourant jaunâtre à l'horizon !"


        #print "Node "+str(self.__id)+" : "+str(self.__result)
        if self.__result is None:
            print "C'est du None !!"
            print self.__result
            quit()
        return self.__result

    # @function      getCorrelation(): 
    def getCorrelation(self):
        if self.__correlation is None:
            if self.__type == 'cte':
                # si c'est une constante, on considère la corrélation comme étant nulle
                self.__correlation = -3
            elif self.__type == 'var':
                # si c'est une variable, on va chercher dans le modèle de reférence la 
                # valeure de la corrélation, qu'on aura calculée une fois pour toute 
                # pour chaque variable
                self.__correlation = Node.refModel.getVariableCorrelation(self.__value)
            elif self.__type == 'link':
                self.__correlation = self.__value.getCorrelation()
            else:
                if any(numpy.isinf(self.getResult())) or any(numpy.isnan(self.getResult())) :
                    # Si il y a des inf, on met une correlation de 0, ce qui permet de ne pas
                    # pas trop pénaliser les arbres qui contienne des operateurs.
                    self.__correlation = -1
                else:
                    # si le noeud est un opérateur, alors on calcul la corrélation avec la méthode de Pearson.
                    # Pour ce faire, on utilisera la fonction de référence normalisée, ce qui 
                    # permet de ne faire qu'une seule fois le calcul de la moyenne et de la variance
                    # de la fonction de référence

                    # Test des variations du result
                    if max(self.getResult())-min(self.getResult()) < 2*MACHINE_EPS:
                        # Si le noeud a un result constant, alors sa correlation est -1
                        self.__correlation = -2
                    else:
                        # Calcul de la std du result
                        nodeStd = numpy.std( self.getResult() )
                        # Calcul du result apres centrage
                        resultCentrage = ( self.getResult() - numpy.mean(self.getResult()) ) 
                        # Calcul de la correlation (sans prise en compte de la std du result)
                        self.__correlation = numpy.mean( resultCentrage * Node.refModel.getRefFunctionNormalised() ) 
                        # On finit par prendre en compte la std de result
                        self.__correlation /= nodeStd
                        # On ne garde que la valeur absolue
                        self.__correlation = abs( self.__correlation )

        
        return self.__correlation

    # ========================= #
    #        AFFICHAGE          #
    # ========================= #

    def getX(self,):
        return self.__x

    def setX(self,x):
        self.__x = x


    def computeX(self):
        if self.isLeaf():
            if self.__x is None:
                raise Exception, 'X undefined for a leaf Node'
        else:
            if self.__type == "bn":
                self.__x = (self.__left.computeX() + self.__right.computeX() ) / 2
            elif self.__type == "un":
                self.__x = self.__left.computeX() 
        return self.__x





    # @function      printTextFormula(): print a tree in the text form
    # @return        a string that contains the expression of tree at the texte form
    def getTextString(self):
        if self.__type == "bn":   
            # we print the operation of two nodes, with the two suns of node
            if self.__value == "^":
                s = "pow(" + str(self.__left.getTextString()) + "," + str(self.__right.getTextString()) + ")"
			# we make the operation of two nodes, with the two suns of node
            else:
                s = "(" + str(self.__left.getTextString()) + str(self.__value) + str(self.__right.getTextString()) + ")"
        elif self.__type == "un":
            s = str(self.__value) + "(" + str(self.__left.getTextString()) + ")"
		# we print the value of node
        elif self.__type == "var":
            s = "x" + str(self.__value)
		# we print the value of node
        elif self.__type == "cte":
            s = str(round(self.__value, 2))
        elif self.__type == "link":
            s = self.__value.getTextString()
        s.replace('+-','-');
        s.replace('--','+');
        return s


    # @function      getLatexString(): print a tree in the latex form
    # @return        a string taht contains the expression of the tree in latex form
    def getLatexString(self):
        if self.__type == "bn":
            if self.__value == "^":
                s = "(" + str(self.__left.getLatexString()) + str(self.__value) + "{" + str(self.__right.getLatexString()) + "}" + ")"
            elif self.__value == "/":
                s = "(\\frac{" + str(self.__left.getLatexString()) + "}{" + str(self.__right.getLatexString()) + "}" + ")"
            else:
                s = "(" + str(self.__left.getLatexString()) + str(self.__value) + str(self.__right.getLatexString()) + ")"
        elif self.__type == "un":
            s = "\\" + str(self.__value) + "(" + str(self.__left.getLatexString()) + ")"
        elif self.__type == "var":
            s = "x_{" + str(self.__value) + "}"
        elif self.__type == "cte":
            s = str(round(self.__value, 2))
        elif self.__type == "link":
            s = self.__value.getLatexString()
        s.replace('+-','-');
        s.replace('--','+');
        return s





