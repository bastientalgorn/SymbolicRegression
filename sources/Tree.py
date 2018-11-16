# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
from Node import *
import random


class Tree():

    # ===========================
    #    v Public Methodes  v
    # ===========================   

    # @function      __init__()
    def __init__(self): 
        self.__rootNode = None
        self.__nodes = []
        self.__nbNodes = 0
        self.__nbLeafs = 0
        self.__nbLevels = 0
        self.__nodesCorrelationOrder = []


    #===================================================#
    #            STRUCTURE ET CERTIFICATION             #
    #===================================================#


    # @function      getNodes():
    def getNodes(self):
        return self.__nodes

    def getResult(self):
        #R = random.random()
        #print ">> in  Tree:getResult ("+str(R)+")"
        #self.printByLevel()
        result = self.__rootNode.getResult()
        #print "<< out Tree:getResult ("+str(R)+")\n\n\n"
        return result
  
    def getCorrelation(self):
        return self.__rootNode.getCorrelation()

    # @function      getNbNodes(): calculate the number of nodes in a tree
    def getNbNodes(self):
        return self.__nbNodes

    # @function      getNbLeafs(): calculate the number of nodes in a tree
    def getNbLeafs(self):
        return self.__nbLeafs

    # @function      getNbLevels(): calculate the number of nodes in a tree
    def getNbLevels(self):
        return self.__nbLevels

    # @function    __eq__ 
    def __eq__(self, other):
        return self.__rootNode == other.__rootNode

    # @function    __setNodeCorrelationOrder   
    def __setNodeCorrelationOrder(self):
        # TODO: rajouter un mode "NoLinkNode" 
        # TODO: faire le tri entre _setNodeCorrelationOrder et sortNodesByCorrelation
        tab = []
        for n in self.__nodes:
            tab.append([n.getCorrelation(), n.getId()])
        tab.sort(cmp=lambda x, y: cmp(x[0], y[0]))
        self.__nodeCorrelationOrder = []
        for n in tab:
            self.__nodeCorrelationOrder.append(n[1]) 

    # @function    getRandomRouletteNode(): select a node based on the strong rate of correlation with biased roulette
    # @return                            : a node 
    def getRandomRouletteNode(self,mode = "strong"):
        self.__setNodeCorrelationOrder()
        tab = self.sortNodesByCorrelation()
        N = self.getNbNodes()

        # distribution de i : favorise les grandes valeurs (ie proche de N)
        r = random.random()
        i = math.ceil(  ( numpy.sqrt( 1 + 4 * r * N * (N+1) )  -1) / 2  ) -1 
        i = int(i)

        # si on veut un noeud weak, il faut au contraire cherche au debut de la table
        if mode == "weak":
            i = N-1-i
        
        # On va donc renvoyer node
        node = tab[i][0]
        while node.getType == 'link':
            node = node.getValue()

        # on renvoit le noeud
        return node



    def getRandomRouletteNodeWeakStrong(self):
        self.__setNodeCorrelationOrder()
        tab = self.sortNodesByCorrelation()
        N = self.getNbNodes()

        # tirage du strong (grand indice => Strong)
        r = random.random() 
        indStrong = math.ceil(  ( numpy.sqrt( 1 + 4 * r * N * (N+1) )  -1) / 2  ) -1 
        indStrong = int(indStrong)

         # tirage du Weak (petit indice => Weak)
        r = random.random()
        indWeak = math.ceil(  ( numpy.sqrt( 1 + 4 * r * N * (N+1) )  -1) / 2  ) -1 
        indWeak = int(indWeak)       
        indWeak = N-1-indWeak

        # On vérifie qu'ils ne sont pas identiques
        if indWeak == indStrong:
            # on diminue le Weak
            if indWeak != 0:
                indWeak -= 1
            else:
                indWeak = 1

        # on renvoit le noeud
        return tab[indWeak][0], tab[indStrong][0]




    # @function      sortNodesByCorrelation(): sorts the individual by correlation rate
    # @return        a list of individuals
    def sortNodesByCorrelation(self):
        liste=[]
        for n in self.getNodes():
            liste.append([n, n.getCorrelation()])
        liste.sort(cmp=lambda x,y: cmp(x[1], y[1]))
        return liste


    #===================================================#
    #                AFFICHAGE BASIC                    #
    #===================================================#



    # @function      getTextString(): 
    def getTextString(self):
        return self.__rootNode.getTextString()

    # @function      getLatexString(): 
    def getLatexString(self):
        return self.__rootNode.getLatexString()



    # @function      printBylevel(): print the tree by level
    #                                the display beagn by the root 
    # @return        None
    def printByLevel(self):
        currentLevel = [self.__rootNode]
        print " "
        print "     --------------------------------------------"
        # if level's array is not None
        while currentLevel:
            print "     |   ",
            nextLevel = list()
            for n in currentLevel:
                # affichage du pere
                if len(n.getFathers())>=2:
                    fatherString = "\033[31m{"
                    for f in n.getFathers():
                        fatherString+= str(f.getId())+","
                    fatherString = fatherString[:-1]+ "}\033[0m"
                elif len(n.getFathers())==1:
                    fatherString = "{"+str(n.getFathers()[0].getId())+"}"
                else:
                    fatherString = "{\033[32mR\033[0m}"

                # affichage de l'id :
                idString = "["+str(n.getId())+"]"
                
                # affichage du contenu : 
                if n.getType() == "var":
                    valueString = "x"+str(n.getValue())
                elif n.getType() == "cte":
                    valueString = str(round(n.getValue(), 2))
                elif n.getType() == "link":
                    valueString = "\033[41mN"+str(n.getValue().getId())+"\033[0m"
                else:
                    valueString = str(n.getValue())

                # print :
                print idString+fatherString+valueString+"  ",

                # construction du niveau inferieur :
                if n.getLeftNode() is not None:
                    nextLevel.append(n.getLeftNode())
                if n.getRightNode() is not None:
                    nextLevel.append(n.getRightNode())
            print 
            currentLevel = nextLevel

        print "     --------------------------------------------"
        print " "


    # @function      printBylevel(): print the tree by level
    #                                the display beagn by the root 
    # @return        None
    def printFancyBackup(self):
        

        # List of all the nodes, with display additional informations
        dataNode = list()
        # List of the number of nodes for each level
        nodeNumberByLevel = list()
    
        levelIndex = 0
        currentLevel = [self.__rootNode]
        print " **************************************** "
        print " in Tree::printFancy "
        self.printByLevel()
        
        # Cumulated sum of the length of the strings of the Leafs
        cumLeafStringLen = 0.0        

        # Distance between nodes
        separationSpace = 6.0

        # if level's array is not None
        while currentLevel:
            print "Gathering data from level "+str(levelIndex)

            # Initialisation for this level
            nextLevel = list()
            
            
            # Memorization of the number of nodes on this level
            if len(currentLevel):
                nodeNumberByLevel.append(len(currentLevel))


            for n in currentLevel:

                ## Construction de la chaîne de caractères
                # Node's Id :
                nString = "["+str(n.getId())+"]"
                # Node's Fathers list
                if len(n.getFathers())>=2:
                    nString += "{"
                    for f in n.getFathers():
                        nString+= str(f.getId())+","
                    nString = nString[:-1]+ "}"
                elif len(n.getFathers())==1:
                    nString += "{"+str(n.getFathers()[0].getId())+"}"
                else:
                    nString += "{R}"
                # Node's contents
                if n.getType() == "var":
                    nString += "x"+str(n.getValue())
                elif n.getType() == "cte":
                    nString += str(round(n.getValue(), 2))
                elif n.getType() == "link":
                    valueString = "N"+str(n.getValue().getId())
                else:
                    nString += str(n.getValue())

                ## Length, X, level, 
                nLen = len(nString) 
                if n.isLeaf():
                    nPos = cumLeafStringLen + float(nLen)/2
                    cumLeafStringLen += 2*separationSpace + len(nString)
                else:
                    nPos = None

                n.setX(nPos)
                nLev = levelIndex
                dataNode.append([n, nLev, nString, nLen])

                # construction du niveau inferieur :
                if n.getLeftNode() is not None:
                    nextLevel.append(n.getLeftNode())
                if n.getRightNode() is not None:
                    nextLevel.append(n.getRightNode())

                    

            currentLevel = nextLevel
            levelIndex += 1

        self.__rootNode.computeX()

        for n in dataNode:
            print n,
            print n[0].getX()


        levelIndex = -1
        for elem in dataNode:
            n = elem[0]
            nLev = elem[1]
            nString = elem[2]
            nLen = elem[3]
            nPos = n.getX()
            if nLev==levelIndex+1:
                levelIndex += 1
                currentPosition = 0
                print "\nNewLevel   :",
            print "_"*int(nPos-currentPosition-nLen/2),
            print nString,
            currentPosition = nPos+nLen+separationSpace                        


        print "\n     --------------------------------------------"
        quit()
        print " "




  

 
    # @function      printBylevel(): print the tree by level
    #                                the display beagn by the root 
    # @return        None
    def printFancy(self):
        
        # List of all the nodes, with display additional informations
        dataNode = list()
        # List of the number of nodes for each level
        nodeNumberByLevel = list()
    
        levelIndex = 0
        currentLevel = [self.__rootNode]
        print " **************************************** "
        print " in Tree::printFancy "
        self.printByLevel()
        
        # Cumulated sum of the length of the strings of the Leafs
        cumLeafStringLen = 0.0        

        # Distance between nodes
        separationSpace = 6.0

        for n in self.getNodes():

            ## Construction de la chaîne de caractères
            # Node's Id :
            nString = "["+str(n.getId())+"]"
            # Node's Fathers list
            if len(n.getFathers())>=2:
                nString += "{"
                for f in n.getFathers():
                    nString+= str(f.getId())+","
                nString = nString[:-1]+ "}"
            elif len(n.getFathers())==1:
                nString += "{"+str(n.getFathers()[0].getId())+"}"
            else:
                nString += "{R}"
            # Node's contents
            if n.getType() == "var":
                nString += "x"+str(n.getValue())
            elif n.getType() == "cte":
                nString += str(round(n.getValue(), 2))
            else:
                nString += str(n.getValue())

            ## Length, X, level, 
            nLen = len(nString) 
            if n.isLeaf():
                nPos = cumLeafStringLen + float(nLen)/2
                cumLeafStringLen += 2*separationSpace + len(nString)
            else:
                nPos = None

            n.setX(nPos)
            dataNode.append([n, nString])



        self.__rootNode.computeX()

        for n in dataNode:
            print n,
            print n[0].getX()



        levelIndex = -1
        for elem in dataNode:
            n = elem[0]
            nString = elem[1]
            nLevel = n.getLevel()
            nLength = len(nString)
            nPos = n.getX()
            if nLevel==levelIndex+1:
                levelIndex += 1
                currentPosition = 0
                print "\nNewLevel   :",
            print "_"*int(nPos-currentPosition-nLength/2),
            print nString,
            currentPosition = nPos+nLength+separationSpace                        


        print "\n     --------------------------------------------"
        #quit()
        print " "

    #===================================================#
    #                 TRAITEMENT                        #
    #===================================================#

    # @function      shortenTree(): replace the value node those have suns are constants with their results
    # @return        None
    def shortenTree(self):
        # look into the contents of tree:
        for node in self.getNodes():
            # if the node is an operator
            if node.getType() in ["bn","un"]:
                # and if the node result is constant,
                rmin = node.getResult().min()
                rmax = node.getResult().max()
                if rmin==rmax:
                    # then the node is changed into a constant one
                    self.resetNode(node, 'cte', rmin)

    # @function      pasteNode(): 
    def pasteNode(self, destinationNode, movedNode):
        
        print "in Tree pasteNode, Duplication de "+str(movedNode.getId())+" vers "+str(destinationNode.getId())
        self.verifyLink()
        if destinationNode not in self.__nodes:
            raise Exception, 'ERROR: Cannot cross external node.'
        # Save father
        fList = destinationNode.getFathers()
        child = []
        for f in fList:
            if destinationNode == f.getLeftNode():
                child.append('L')
            elif destinationNode == f.getRightNode():
                child.append('R')
            elif destinationNode == f.getValue():
                child.append('V')

        # Duplication  du noeud
        nbLeafOld = len(destinationNode.getAllLeafs())
        newNode, nodeList, nbLeaf, nbLvl = movedNode.duplicate()
        for i, f in enumerate(fList):
            if child[i] == 'L':
                f.setLeftNode(newNode)
            elif child[i] == 'R':
                f.setRightNode(newNode)
            elif child[i] == 'V':
                f.setValue(newNode)

        newNode.setFathers(fList)
        self.resetNodeStatut(newNode)

      
        self.__recomputeIds()
        self.__resetResults(fList)


        self.getResult()
        self.printByLevel()
        self.verifyLink()
        print "Fin de Tree:pasteNode"



    # @function      linkNode(): 
    def linkNode(self, destinationNode, movedNode):
            
        print "in Tree linkNode, link de "+str(movedNode.getId())+" vers "+str(destinationNode.getId())
        self.verifyLink()

        if destinationNode not in self.__nodes:
            raise Exception, 'ERROR: Cannot cross external node.'

        destinationNode.setType('link')
        destinationNode.setValue(movedNode)
        destinationNode.setLeftNode(None)
        destinationNode.setRightNode(None)

        movedNode.addFather(destinationNode)

        self.resetNodeStatut(destinationNode)
  
        # Vérification
        self.verifyLink()
        self.getResult()
        print "Fin de Tree:pasteNode"



    def verifyLink(self):
        self.resetNodeStatut(self.__rootNode)
        self.printByLevel()
        for n in self.__rootNode.getAllNodes():
            print "        n"+str(n.getId())+" "+str(id(n))+" "+str(n.getType())    
            print "            enfants :"
            # Verification that each child of n knows that n is its father
            # left child
            if n.getLeftNode() is not None:
                if n not in n.getLeftNode().getFathers():
                    print "n LEFT node has no reference to n"
                    print str(n)
                    ERREUR
                else:
                    child = n.getLeftNode()
                    print "               L"+str(child.getId())+" "+str(id(child))
            # right child
            if n.getRightNode() is not None:
                if  (n not in n.getRightNode().getFathers()):
                    print "n RIGHT node has no reference to n"
                    print str(n)
                    ERREUR
                else:
                    child = n.getRightNode()
                    print "               R"+str(child.getId())+" "+str(id(child))
            # link child
            if n.getType()=="link":
                """
                print "[ father du link : ",
                for f in n.getValue().getFathers():
                    print str(f.getId())+"&",
                print "]",
                """
                if n not in n.getValue().getFathers():
                    print "n LINK node has no reference to n"
                    print str(n)
                    ERREUR
                else:
                    child = n.getValue()
                    print "               V"+str(child.getId())+" "+str(id(child))

            # verification that each father of n knows that n is its child

            print "            parents :"
            for f in n.getFathers():
                isRecognised = False
                # as left child
                if (f.getLeftNode() is not None)   and   (n == f.getLeftNode()):
                    isRecognised = True
                    tag = "/L"
                # as right child
                if (f.getRightNode() is not None)  and   (n == f.getRightNode()):
                    isRecognised = True
                    tag = "/R"
                # as link child
                if (f.getType()=="link")           and   (n == f.getValue()):
                    isRecognised = True
                    tag = "/V"

                if not isRecognised:
                    print "n has a father f that has no reference to n"
                    print "n : "+str(n)
                    print "f : "+str(f)
                    ERREUR
                else:
                    print "               f"+str(f.getId())+tag+" "+str(id(f))+" "

            print
        print "         ... Verify : OK"



    def __recomputeIds(self):
        for i, node in enumerate(self.__nodes):
            node.setId(i)

    # @function      __resetResults()
    def __resetResults(self, nodes):
        #print "Tree __resetResults"
        for node in nodes:
            #print "Id:"+str(node.getId())+" Type:"+str(node.getType())+" Value:"+str(node.getValue())
            if node.isResultNone():  
                # Si le resultat était déjà à None, on reset quand même le noeud
                # (parce que ça remet à none le Result mais aussi la correlation)
                # Mais on ne s'occupe pas de ses parents.
                node.resetResult()
            else:
                #print "rec"
                # Si le noeud n'est pas à none, on le met à none et on s'occupe ensuite de ses parents         
                node.resetResult()
                fathers = node.getFathers()
                self.__resetResults(fathers)



    # @function      getRandomNodeIndex()
    def getRandomNodeIndex(self):
        return random.randint(0,self.getNbNodes()-1)
 
    # @function      getRandomNode()
    def getRandomNode(self):
        return self.__nodes[self.getRandomNodeIndex()]

    def getRandomLeaf(self):
        i = self.getRandomNodeIndex()
        node = self.getNodes()[i]
        while not node.isLeaf():
            i = self.getRandomNodeIndex()
            node = self.getNodes()[i]
        return node    

    #===================================================#
    #                     CREATION                      #
    #===================================================#

    def createRandomTree(self):
        self.__rootNode = Node()
        self.__nbNodes, self.__nodes, self.__nbLeafs, self.__nbLevels = self.__rootNode.recursiveRandomNode(1)
        self.__nbNodes = len(self.__nodes)
        self.__recomputeIds()
        self.__nodesCorrelationOrder = []

    # @function      duplicate(): copies contents of a tree from another tree
    def duplicate(self):
        newTree = Tree()
        rootNode, nodes, nbLeafs, nbLevels = self.__rootNode.duplicate()
        newTree.__rootNode = rootNode
        newTree.__nodes = nodes
        newTree.nbLeafs = nbLeafs
        newTree.nbLevels = nbLevels
        newTree.__nbNodes = len(newTree.__nodes)
        newTree.__nodesCorrelationOrder = self.__nodesCorrelationOrder
        return newTree

    #===================================================#
    #           SCHEMA DES ARBRES EN LATEX              #
    #===================================================#


    # @function      setLevelForPrint(): assign a level at the diffrent nodes
    #                                    of tree to facilate print of tree using Latex
    def setLevelForPrint(self, level):
        # ???
        # set level to node's root
        self.level = level
        if self.getLeftNode():
            # set level to left sun of node with a lag of 16
            self.getLeftNode().setLevelForPrint(level - 16)    
        if self.getRightNode():
            # set level to right sun of node with lag of 16
            self.getRightNode().setLevelForPrint(level - 16)   


    # @function      setCoordForPrint(): assign the coordinates at the diffrent nodes of tree 
    # @return        None
    def setCoordForPrint(self, level):
        tab = self.getNodes()
        listLeaf = []
        listOperator = []
        # fill a leaf's and operator's arrays
        for elem in tab:
            if elem.isLeaf() == 0:
                listLeaf.append(elem)
            else:
                listOperator.append(elem)
        # set coordinates to leafs
        for i in range(len(listLeaf)):
            listLeaf[i].x = float(i * 12) 
        # set cordinates to operators
        for op in listOperator:
            if op.type == "un":
                op.x = op.left.x
            elif op.type == "bn":
                op.x = float(op.left.x + op.right.x) / 2


    # @function      printLatexDrawing(): print a tree in a latex file
    # @return        a string that contains the latex code of the tree
    def printLatexDrawing(self):
        self.setLevelForPrint(0)
        self.setCoordForPrint(0)
        file = open("..\\AffichageArbreLatex\\AffichageLatex.txt", "w")
        s = ""
        tab = self.getNodes()
        listLeaf = []
        listOperator = []
        listLevel = []

	# fill the level's array
        for elem in tab:
            listLevel.append(elem.level)
        levelOp = max(listLevel)
        
        # fill the leaf's array
        for elem in tab:
            if elem.isLeaf() == 0:
                listLeaf.append(elem)
            else:
                listOperator.append(elem)
        
	# writting the cordinates of leafs
        for leaf in listLeaf:
            if leaf.getType() == "var":
                s += "\Var{" + str(leaf.getX()) + "}{" + str(leaf.getLevel()) + "}{$x_" + str(leaf.getValue()) + "$}" + str('\r')

            elif leaf.getType() == "cte":
                s += "\Cste{" + str(leaf.getX()) + "}{" + str(leaf.getLevel()) + "}{" + str(round(leaf.getValue(),2)) + "}" + str('\r')
		# writting the cordinates of operators		
        for op in listOperator:
            opx = op.x
            if op.left:
                oplx = op.left.x
                opll = op.left.level
            if op.right:
                oprx = op.right.x
            
			# tests if node has a unary type
            if op.type == "un":
                if op.level == levelOp:
                    s += "\OpRoot{" + str(opx) + "}{" + str(opll + 12) + "}{$" + op.value + "$}" + str('\r')
                else:
                    s += "\Op{" + str(opx) + "}{" + str(opll + 12) + "}{$" + op.value + "$}" + str('\r')
			# tests if node has a ubinary type
            elif op.type == "bn":
                if op.level == levelOp:
                    if op.value == "^":
                        s += "\OpRoot{" + str(opx) + "}{" + str(opll + 12) + "}{$" + str("pow") + "$}" + str('\r')
                        s += "\put( " +  str(oplx) + "," + str(opll + 12) + "){\line(1,0){" + str(oprx - oplx) + "}}" + str('\r')
                    else:
                        s += "\OpRoot{" + str(opx) + "}{" + str(opll + 12) + "}{$" + str(op.value) + "$}" + str('\r')
                        s += "\put(" +  str(oplx ) + "," + str(opll + 12) + "){\line(1,0){" + str(oprx - oplx) + "}}" + str('\r')                    
                else:
                    if op.value == "^":
                        s += "\Op{" + str(opx) + "}{" + str(opll + 12) + "}{$" + str("pow") + "$}" + str('\r')
                        s += "\put( " +  str(oplx) + "," + str(opll + 12) + "){\line(1,0){" + str(oprx - oplx) + "}}" + str('\r')
                    else:
                        s += "\Op{" + str(opx) + "}{" + str(opll + 12) + "}{$" + str(op.value) + "$}" + str('\r')
                        s += "\put(" +  str(oplx ) + "," + str(opll + 12) + "){\line(1,0){" + str(oprx - oplx) + "}}" + str('\r')                    
        file.write(s)
        file.close()
        return s
                   

    # -------------------------------------


    def mutationIsoType(self, biased=False):
        # Choice of the node to be mutated
        if biased:
            n = self.getRandomRouletteNode("weak")
        else:
            n = self.getRandomNode()
        # Choice of the new value
        if n.getType() == "bn":
            n.setValue(random.choice(Node.getBnOp()))
        elif n.getType() == "un":
            n.setValue(random.choice(Node.getUnOp()))
        elif n.getType() == "var":
            n.setValue(Node.getRandomVariableIndex())
        elif n.getType() == "cte":
            n.setValue(n.getValue() + Node.symetricExp())
        # As the node has been mutated, all results above
        # this node have to be set to none
        self.__resetResults([n]) 

    def resetRandomNode(self, newType, newValue):
        n = self.getRandomNode()
        self.resetNode(n, newType, newValue)

    def resetNode(self, node, newType, newValue):
        node.reset(nodetype=newType, value=newValue)
        self.resetNodeStatut(node)


    def resetNodeStatut(self, node):
        self.__resetResults([node])

        self.__nbLeafs = len(self.__rootNode.getAllLeafs())
        self.__nbLevels = self.__rootNode.getDepth()
        self.__nodes = self.__rootNode.getAllNodes()
        self.__nbNodes = len(self.__nodes)
        self.__recomputeIds()










