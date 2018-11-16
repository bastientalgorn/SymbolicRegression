# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-

from PYGA_StandardMultiObjIndividual_NSGAII import PYGA_StandardMultiObjIndividual_NSGAII

import random
import sys
import numpy

from RefModel import RefModel
from Node import Node
from Tree import Tree


class Individual(PYGA_StandardMultiObjIndividual_NSGAII):

    NB_OBJECTIVES = 2

    def __init__(self):
        self.__tree = Tree()
        PYGA_StandardMultiObjIndividual_NSGAII.__init__(self)

    @classmethod
    def generate(cls):
        # 1- Create the new individual
        newInd = cls()
        # 2- Generate each variable
        newInd.__tree.createRandomTree()
        # 3- Return the generated individual...
        return newInd

    def __str__(self):
        strObj = str(self.getObj()).replace('[', '').replace(']', '')
        strResult = str(self.__tree.getResult())
        return strObj #+ ', ' + strResult

    def objectives(self, population):
        comp = self.getComplexity()
        err = self.getError()
        cor = self.getCorrelation()
        obj1 = 1 - cor
        obj2 = comp
        self.setObj( [ obj1 , obj2 ] )

    def getError(self):        
        nbPoints = Node.refModel.getNbPoints()
        difference = self.__tree.getResult() - Node.refModel.getRefFunction()
        return numpy.sqrt(numpy.sum(pow(difference,2)) / nbPoints)

    def getComplexity(self):
        return self.__tree.getNbNodes()

    def getResult(self):
        return self.__tree.getResult()

    def getCorrelation(self):
        return self.__tree.getCorrelation()

    def getTextString(self):
        return self.__tree.getTextString()

    def __eq__(self,other):
        return (self.__tree == other.__tree)


    # ==================================== #
    #         CROSSOVER METHODES           #
    # ==================================== #
    @classmethod
    def crossover(cls, parent1, parent2):
        print "in Crossover"
        parent1.__tree.printByLevel
        parent2.__tree.printByLevel
        # Create the new individual
        newInd = cls()
        # Start from parent1 as tree base
        newInd.__tree = parent1.__tree.duplicate()
        # Choose a random node to replace
        n1 = newInd.__tree.getRandomNode()
        # Do not replace root node
        while n1.getFathers() is None:
            n1 = newInd.__tree.getRandomNode()
        # Choose a node from parent2 to duplicate
        n2 = parent2.__tree.getRandomNode()
        # Paste the node n2 into newInd
        newInd.__tree.pasteNode(n1, n2)
        newInd.__tree.verifyLink()
        newInd.setObj(None)
        return newInd


    # ==================================== #
    #          MUTATION METHODES           #
    # ==================================== #
    @classmethod
    def mutation(cls, individual):
        # Copy of the individual
        newInd = cls()
        newInd.__tree = individual.__tree.duplicate()
        N = newInd.__tree.getNbNodes()
        tabProba = numpy.empty(7,'float32')
        # nb : CU veut dire "Condition d'Utilisation"

        # OP 0: mutationIsoType (Operateur de base) :
        #       CU : Néant
        tabProba[0] = 0.4

        # OP 1: operateur mutationLeaf2Leaf :
        #       CU : Néant
        tabProba[1] = 0.4

        # OP 2: mutationLeaf2Op (Bloom) :
        #       CU : Néant. Fav
        #       Favorisé si il y a 2 noeuds ou moins
        tabProba[2] = 0.3 + 0.3 * (N<=2)

        # OP 3: mutationIsoTypeRouletteBiaisee :
        #       CU : Au moins 3 noeuds
        tabProba[3] = 0.5 * (N>=3)

        # OP 4: mutationInternCrossover (Ramification interne) :
        #       CU : Au moins 4 noeuds
        tabProba[4] = 10*0.7 * (N>=4)

        # OP 5: mutationShortenTree (Simplification) :
        #       CU : Au moins 6 noeuds
        tabProba[5] = 0.1 * max(0,N-5)

        # PO 6: mutationNode2Leaf (Raccourci) :
        #       CU : Au moins 4 noeuds
        tabProba[6] = 0.1 * max(0,N-3)

        tabProba = tabProba.cumsum()
        tabProba /= tabProba[-1]
        
        r = random.random()
        if r < tabProba[0]:
            newInd.mutationIsoType()
        elif r < tabProba[1]:
            newInd.mutationLeaf2Leaf()
        elif r < tabProba[2]:
            newInd.mutationLeaf2Op()
        elif r < tabProba[3]:
            newInd.mutationIsoTypeRouletteBiaisee()
        elif r < tabProba[4]:
            newInd.mutationInternCrossover()
        elif r < tabProba[5]:
            newInd.mutationShortenTree()
        elif r < tabProba[6]:
            newInd.mutationNode2Leaf()
        else:
            error('O flots que vous savez de lugubres histoires !');

        newInd.setObj(None)
        #print newInd.__tree.printFancy()
        newInd.__tree.verifyLink()
        return newInd


    # Mutation - OP 0
    # Choice of a node uniformly.
    # Change its value but not its type.
    def mutationIsoType(self):
        self.__tree.mutationIsoType(biased=False)
    

    # Mutation - OP 1
    # Mutation : Remplace une feuille par une autre feuille
    def mutationLeaf2Leaf(self):
        n = self.__tree.getRandomLeaf()
        n.setRandomLeaf()
        self.__tree.resetNode(n, n.getType(), n.getValue() )


    # Mutation - OP 2
    # Bloom !.
    def mutationLeaf2Op(self):
        n = self.__tree.getRandomLeaf()

        # Fils gauche
        nLeft = Node()
        nLeft.setRandomLeaf()
        nLeft.setFathers([n])

        if random.random() <0.4:
            # Opérateur Binaire
            nType = 'bn'
            nValue = random.choice(Node.getBnOp())
            # Fils droit
            nRight = Node()
            nRight.setRandomLeaf()
            nRight.setFathers([n])
        else:
            # Opérateur Unaire
            nType = 'un'
            nValue = random.choice(Node.getUnOp())
            nRight = None
            
        n.reset(nType, nValue, nLeft, nRight, None, 0)
        self.__tree.resetNodeStatut(n)

        

    # Mutation - OP 3
    # Choice of a node with weak correlation.
    # Change its value but not its type.
    def mutationIsoTypeRouletteBiaisee(self):
        self.__tree.mutationIsoType(biased=True)


    # Mutation - OP 4
    # Mutation by intern crossover
    def mutationInternCrossover(self):

        if self.__tree.getNbNodes()==1:
            raise Exception, 'ERROR: mutationInternCrossover cannot be used if tree has only one node'
        print "*** Intern Crossover ***"
        
        nodeWeak , nodeStrong = self.__tree.getRandomRouletteNodeWeakStrong()
        #if (random.random() < 0.5) or nodeStrong.isAncestor(nodeWeak):
        if nodeStrong.isAncestor(nodeWeak) or nodeWeak.isAncestor(nodeStrong):
        #if True:
            self.__tree.pasteNode(nodeWeak,nodeStrong)
        else:
            self.__tree.linkNode(nodeWeak,nodeStrong)

    # Mutation - OP 5
    # Shorten the constant branch of tree
    def mutationShortenTree(self):
        self.__tree.shortenTree()


    # Mutation - OP 6
    # Mutation : Remplace un noeud par une feuille
    def mutationNode2Leaf(self):
        if random.random() < 0.5:
            newType = 'cte'
            if random.random() < 0.5:
                newValue = Node.symetricExp()
            else:
                newValue = numpy.mean(self.getResult())
        else:
            newType = 'var'
            newValue = Node.getRandomVariableIndex()

        self.__tree.resetRandomNode(newType, newValue)
        

        
