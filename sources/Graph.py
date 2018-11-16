# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-
import random
import math
import numpy
import os
import util
import operator
from OpManager import OpManager
from Node import Node

numpy.seterr(all='ignore')

LOG_H_LIMIT = 6
CHECK = False
PRINT = False
METICULOUS_COMPARE = False

class Graph():

    # =============================================
    # classmethod relative to the operator list
    # =============================================

    __OP_MANAGER = OpManager()

    __REF_MODEL = None
    __NB_POINTS = None
    __REF_FUNC = None
    __REF_FUNC_MEAN = None
    __REF_FUNC_STD = None

    __VAR_VALUES = None
    __VAR_COR = None

    __METHOD_POST_PROCESSING = None
    __METHOD_OBJECTIVE_ERROR = None

    __WORSE_ERROR = None
    #__OP_MAX_NB_ARG = None
    #__OP_MANAGER = None



    @classmethod
    def setRefModel(cls, refModel):
        cls.__REF_MODEL = refModel
        cls.__NB_POINTS = refModel.getNbPoints()
        cls.__REF_FUNC = refModel.getRefFunction()
        cls.__REF_FUNC_MEAN = refModel.getRefFunctionMean()
        cls.__REF_FUNC_STD = refModel.getRefFunctionStd()
        cls.__VAR_VALUES = []
        cls.__VAR_COR = []
        for var in xrange(refModel.getNbVariables()):
            cls.__VAR_VALUES.append(refModel.getVariable(var))
            cls.__VAR_COR.append(refModel.getVariableCorrelation(var))

    @classmethod
    def opListLoad(cls, fileName):
        cls.__OP_MANAGER.loadOpFile(fileName)
        cls.__OP_MAX_NB_ARG = cls.__OP_MANAGER.getMaxNbArg()


    # This two variables allow to monitor the number of 
    # node calculation compared to the number of call
    # to the node H
    __NODE_H_CALCULATION = 0
    __NODE_H_CALL = 0
    @classmethod
    def getNodeHCalculation(cls):
        return cls.__NODE_H_CALCULATION

    @classmethod
    def getNodeHCall(cls):
        return cls.__NODE_H_CALL

    @classmethod
    def printOperatorList(cls):
        cls.__OP_MANAGER.printOperatorList()


    # ===========================
    #    v Public Methodes  v
    # ===========================   

    def __init__(self): 
        self.__nodes = [] 
        self.__tensor = numpy.zeros([0,0,self.__OP_MAX_NB_ARG],dtype=bool)     
    #===================================================#
    #             DUPLICATE  & CONCATENATE              #
    #===================================================#

    # Return a copy of the graph
    def duplicate(self):
        newGraph = Graph()
        newGraph.__nodes = []
        for node in self.__nodes:
            newGraph.__nodes.append(node.duplicate())

        newGraph.__tensor = numpy.copy(self.__tensor)
        return newGraph
        

    # Create a new graph gn by concatenation of 2 graphs g1 & g2
    # All the nodes from g2 are not connected to the root of gn
    @classmethod
    def concatenate(cls,g1,g2):
        n1 = g1.getNbNodes()
        n2 = g2.getNbNodes()
        nn = n1+n2
        gn = g1.duplicate()
    
        # Concatenation of the nodes
        for node in g2.__nodes:
            gn.__nodes.append(node.duplicate())
    
        # Concatenation of the tensors
        # The final tensor Gn will be:
        gn.__tensor = numpy.zeros([nn,nn,Graph.__OP_MAX_NB_ARG],dtype=bool)
        gn.__tensor[0:n1  , 0:n1  ,:] = g1.__tensor
        gn.__tensor[n1:nn , n1:nn ,:] = g2.__tensor

        return gn

    def deleteUselessNodes(self):
        nb = self.getNbNodes()
        U = self.getUselessVector()
        # iterate over nodes backward
        for i in range(nb-1,-1,-1):
            # If note i is useless...
            if U[i]:
                self.__nodes.pop(i)
                self.__tensor = numpy.delete(self.__tensor,i,0)
                self.__tensor = numpy.delete(self.__tensor,i,1)
            

    def checkConsistency(self,position):
        if PRINT:
            print "Graph.checkConcistensy in "+position

        # Utility function that can be used during debug to check the consistency
        # between nodes and the tensor
        nb = self.getNbNodes()
        consistency = True
        S = self.__tensor.shape
        if (nb<1) or (S[0]!=nb) or (S[1]!=nb) or (S[2]!=self.__OP_MAX_NB_ARG):
            print "Nodes number: "+str(nb)
            print "Op max nbArg: "+str(self.__OP_MAX_NB_ARG)
            print "Shape: "+str(S)
            print "Dimension error !!"
            consistency = False

        # Verification of the H and logHMax value for each node
        tabH1 = []
        tabLogHMax1 = []
        for i in range(nb):
            tabH1.append(self.getH(i))
            tabLogHMax1.append(self.getLogHMax(i))
        for n in self.__nodes:
            n.resetH()
        for i in range(nb):
            # Check H for node i
            h2 = self.getH(i)
            if util.isDiff(tabH1[i],h2):
                print "Inconsistent H for node "+str(i)
                consistency = False
            # Check logHMax for node i
            logHMax2 = self.getLogHMax(i)
            if util.isDiffScalar(tabLogHMax1[i],logHMax2):
                print "Inconsistent logHMax for node "+str(i)
                consistency = False



        for i in range(nb):
            # Check that type, NbArg, and real number of children are coherent
            n = self.__nodes[i]
            nType = n.getType()
            nNbArg = n.getNbArg()
            nValue = n.getValue()
            # Count of the number of children
            nNbChildren = numpy.count_nonzero(self.__tensor[i,:,:])
            if (nNbArg != nNbChildren):
                print "Node "+str(i)+": unconsistent number of children !"
                print "               Type: "+nType
                print "              nbArg: "+str(nNbArg)
                print "         nbChildren: "+str(nNbChildren)
                consistency = False

            if (nType == "op"):
                if (nNbArg == 0):
                    print "Node "+str(i)+" is an Operator and has no children !"
                    consistency = False
                if not self.__OP_MANAGER.exists(nValue,nNbArg):
                    print "Node "+str(i)+" is an Op, has value \""+str(nValue)+ "\" and "+str(nNbArg)+" args !"
                    consistency = False
            elif (nType == "cte"):
                if (nNbArg!=0):
                    print "Node "+str(i)+" is a "+nType+" and has "+str(nNbArg)+" child(ren) !"
                    consistency = False
                if not ( isinstance(nValue, numpy.ndarray) ):
                    print "Node "+str(i)+" is a Cte and has value: "+str(nValue)+ " !"
                    consistency = False
            elif (nType == "var"):
                if not (nValue in range(Graph.getNbVariables())):
                    print "Node "+str(i)+" is a Var and has value: "+str(nValue)+ " !"
                    consistency = False

        if not consistency:
            print "#========================================="
            print "Lack of consistency !"
            self.printLinks()
            print "checkConsistency is called from: "+str(position)
            print "Exit."
            ERROR



    # ===========================
    #   Create Random Graph 
    # ===========================   


    @classmethod
    def createRandomGraph(cls,nbNodesLimit=20):

        if CHECK and nbNodesLimit < 5:
            print "Error in Graph: createRandomGraph"
            print "nbNodesLimit = "+str(nbNodesLimit)
            nbNodesLimit = 5

        newGraph = cls()

        # Creation of the first node
        newNode = Node.randomNode(cls.__OP_MANAGER, range(cls.getNbVariables()))
        newGraph.addNode(newNode)
        newNodeIndex = 0
        pile = [newNodeIndex]
        
        while len(pile):
            parentIndex = pile.pop(0)
            parentNode = newGraph.__nodes[parentIndex]  
            parentNbArg = parentNode.getNbArg()
            # Create as many children as necessary
            for na in range(parentNbArg):
                # Creation of the new node (randomly)
                newNode = Node.randomNode(cls.__OP_MANAGER, range(cls.getNbVariables()))
                # Addition of the node in the graph
                newGraph.addNode(newNode)
                # Calculation of the index of this node
                newNodeIndex = newGraph.getNbNodes()-1
                # Link of this node with the parent
                newGraph.__tensor[parentIndex,newNodeIndex,na] = True
                # Addition of this index in the pile                
                pile.append(newNodeIndex)
        if CHECK:
            newGraph.checkConsistency("createRandomGraph (1)")
        
        while newGraph.getNbNodes() > nbNodesLimit:
            # Shorten graph if too big
            newGraph.mutationOp2Leaf()
            if CHECK:
                newGraph.checkConsistency("createRandomGraph (2)")
        while newGraph.getNbNodes() < 5:
            # Bloom graph if too small
            newGraph.mutationLeaf2Op()
            if CHECK:
                newGraph.checkConsistency("createRandomGraph (3)")

        return newGraph



    @classmethod
    def loadGraph(cls,fileName):

        # Read the file
        print "  Loading: "+fileName
        fid = open(fileName)
        lines = fid.readlines()
        fid.close()

        # Clean the lines
        lines = util.cleanLines(lines)

        # Get graph field
        fieldGraph = util.getField(lines,"graph")
        for i in range(len(fieldGraph)):
            fieldGraph[i] = fieldGraph[i].split(' ') 
        
        # Get Nb Nodes
        nbNodes = int(util.getField(lines,"NodesNumber")[0])

        # Graph Construction
        g = Graph()
        g.__nodes = nbNodes*[None]
        g.__tensor = numpy.zeros([nbNodes,nbNodes,g.__OP_MAX_NB_ARG],dtype=bool)     
        
        nodeDescriptions = []
        nodeLiaisons = []
        for e in fieldGraph:
            if e[0] == "node":
                nodeIndex = int(e[1])
                nodeType = e[2]
                if nodeType == "cte":
                    nodeValue = float(e[3])
                elif nodeType == "var":
                    nodeValue = int(e[3][-1:])
                elif nodeType == "op":
                    nodeValue = e[3]
                else:
                    print "ERROR: node parameters are not recognized"
                    return
                g.__nodes[nodeIndex] = Node(nodeType,nodeValue,None)
            else:
                # If there is definition of links, then the previous node MUST
                # be an op. Check for this.
                if not nodeType == "op":
                    print "ERROR: Links are defined for a non-op node"
                    return
                
                i = int(e[0])
                j = int(e[1])
                k = int(e[2])
                if k <= cls.__OP_MAX_NB_ARG:
                    g.__tensor[i,j,k] = True
                else:
                    print "ERROR: Definition of link "+str(i)+"->"+str(j)+"("+str(k)+")"
                    print "but maxNbArg = "+str(cls.__OP_MAX_NB_ARG)
                    return
                
        # Second loop for affectation of nbArg and checks
        for i in range(nbNodes):
            n = g.__nodes[i]
            iValue = n.getValue()
            iType = n.getType()
            nbArg = numpy.count_nonzero(g.__tensor[i,:,:])

            n.setNbArg(nbArg)
            n.resetH()

            if iType == "op":
                # Check validity of this operator with this nbArg:
                if not cls.__OP_MANAGER.exists(iValue,nbArg):
                    print "ERROR: node "+str(i)+" is defined as operator \""+iValue+"\""
                    print "and has "+str(nbArg)+" links"
                    if cls.__OP_MANAGER.exists(iValue):
                        print "but this operator is not defined with this nbArg."
                    if cls.__OP_MANAGER.exists(iValue):
                        print "but this operator is not defined."
                    print "Check in the operatorList file"
                    return
                    
            if iType == "var":
                # check that the variable index is allowed
                if not iValue in range(cls.getNbVariables()):
                    print "ERROR: node "+str(i)+" is defined as variable x"+str(iValue)
                    print "but there is no such variable in reference model"
                    return
        return g




    # ===========================
    #    Set & Get
    # ===========================      

    def getNbNodes(self,nodeIndex=0):
        if nodeIndex == 0:
            return len(self.__nodes)
        else:
            D = self.getDescendantsMatrix()
            return 1+numpy.count_nonzero(D[nodeIndex,:])

    @classmethod
    def getNbVariables(cls):
        return cls.__REF_MODEL.getNbVariables()

    def getFullNbNodes(self,nodeIndex=0):
        # Return the equivalent number of nodes if there was no multiple links
        fnb = 1
        if not self.__nodes[nodeIndex].isLeaf():
            children = self.getChildrenIndex(nodeIndex)
            for c in children:
                fnb += self.getFullNbNodes(c)
        return fnb

    def getNbLinks(self):
        return numpy.count_nonzero(self.__tensor)

    def resetAncestors(self,nodeIndex):
        # Reset all the ancestors of nodeIndex
        # but not nodeIndex itself.
        D = self.getDescendantsMatrix()  
        ancestorsIndexes = numpy.nonzero(D[:,nodeIndex])[0]
        for i in ancestorsIndexes:
            self.__nodes[i].resetH()

    def resetBranch(self,nodeIndex):
        # Reset nodeIndex and all his ancestors
        self.__nodes[nodeIndex].resetH()
        self.resetAncestors(nodeIndex)    

    def resetAll(self):
        for n in self.__nodes:
            n.resetH()

    def getBestNodeIndex(self):
        # Return the index of the node with the best (greatest) correlation.
        # If several nodes have the best correlation, the one with the less descendants 
        # is returned.
        criteriaList = self.getNodeCriteriaList()
        criteriaMin = min(criteriaList)
        nbNodesMin = self.getNbNodes()
        for i in range(self.getNbNodes()):
            ni = self.getNbNodes(i)
            if criteriaList[i] == criteriaMin and ni <= nbNodesMin:
                iCriteriaMin = i
                nbNodesMin = ni
        return iCriteriaMin

    def isScalar(self,i=0):
        h = self.getH(i) 
        return len(numpy.atleast_1d(h))==1

    def isConstant(self,i=0):
        n = self.__nodes[i]
        # cte leafs are constant
        if n.getType() == "cte":
            return True
        # Var leafs are NOT constant
        if n.getType() == "var":
            return False
        # H is scalar
        if self.isScalar(i):
            return True
        # the node's H is not defined => Constant
        h = self.getH(i)   
        if h is None:
            return True
        # the magnitude of r is smaller than EPS => Constant
        if not util.isDiffScalar(numpy.min(h),numpy.max(h)):
            return True
        # all children of the node are constant => Constant
        # nb: this criteria is very very unlikely to be satisfied
        allChildrenConstant = True 
        for j in self.getChildrenIndex(i):
            allChildrenConstant = allChildrenConstant and self.isConstant(j)
        if allChildrenConstant:
            return True
        # Otherwise => NOT Constant
        return False
        



    # ========================= #
    #          MATRIX           #
    # ========================= #    

    def getAdjacencyMatrix(self):
        # Return the adjacency Matrix B
        # B(i,j) = True <=> j is a direct child of i
        # The difference with tensor is that we don't
        # know if j is the 1st or 2nd argument of i
        nb = self.getNbNodes()
        B = numpy.zeros( [nb,nb] , dtype=bool )
        for k in range (self.__OP_MAX_NB_ARG):
            B += self.__tensor[:,:,k]
        return B

    def getDescendantsMatrix(self):
        # Return the matrix D, such that:
        # D(i,j) == True <=> j is a descendant of i
        # nb: a node is not a descenant of itself, except if there are 
        # cycles in the graph (which is not wanted)
        nb = self.getNbNodes()
        D = numpy.copy( self.getAdjacencyMatrix() )
        Dold = numpy.zeros( [nb,nb] , dtype=bool )
        count = 0
        while numpy.any(D != Dold):
            Dold = numpy.copy(D)
            D = D+numpy.dot(D,D)
            count+=1
            if count > nb:
                print "Boucle infinie in Graph.getDescendantsMatrix()"
        return D

    def getCousinsMatrix(self):
        # Return matrix C:
        # C(i,j) <=> i and j are cousins
        # Matrix C is symmetric

        # i and j are cousins if the 3 conditions are satisfied:
        # 1 - i is not a descendant of j
        # 2 - j is not a descendant of i
        # 3 - i != j

        # Two brothers are considered as being cousins.
        # The root node never has a cousin
        nb = self.getNbNodes()
        D = self.getDescendantsMatrix()
        I = numpy.eye( nb , dtype=bool )
        nonD = numpy.logical_not(D)
        nonDprime = numpy.transpose(nonD)
        nonI = numpy.logical_not(I)
        C = nonD * nonDprime * nonI
        return C  

    def getHasCousinsVector(self):
        nb = self.getNbNodes()
        C = self.getCousinsMatrix()
        HC = numpy.zeros(nb,dtype=bool)
        for i in range(nb):
            HC[i] = numpy.any(C[i,:])
        return HC

    def getIsLeafVector(self):
        # return a boolean row vector L
        # L(i) <=> i is a Leaf Node
        nb = self.getNbNodes() 
        L = numpy.zeros(nb,dtype=bool)
        for i in range(nb):
            L[i] = self.__nodes[i].isLeaf()
        return L

    def getUselessVector(self):
        # return a boolean row vector U
        # U(i) <=> not ( i is a descendant of root or i is root)
        D = self.getDescendantsMatrix()
        U = D[0,:]
        U = numpy.logical_not(U)
        U[0] = False
        return U

    def getDepthList(self):
        nb = self.getNbNodes()
        R = numpy.ones((nb),dtype=int)*nb
        k = 0
        B = self.getAdjacencyMatrix()
        V = numpy.zeros((nb),dtype=bool)
        V[0] = True
        while numpy.any(V):
            for i in range(nb):
                if V[i]:
                    R[i] = k
            k += 1
            V = numpy.dot(V,B)
        return R

    #===================================================#
    #                    STRUCTURE                      #
    #===================================================#



    def addNode(self,node):
        nb = self.getNbNodes()
        self.__nodes.append(node)
        self.__tensor = numpy.insert ( self.__tensor , nb , 0 , axis=0 )
        self.__tensor = numpy.insert ( self.__tensor , nb , 0 , axis=1 )


    def getChildrenIndex(self,nodeIndex):
        
        # Method NEW 1
        #A,B = numpy.nonzero(self.__tensor[nodeIndex,:,:])
        #return [x for (y,x) in sorted(zip(B,A))] 

        # Method NEW 2
        #A,B = numpy.nonzero(self.__tensor[nodeIndex,:,:])
        #children = [None]*len(A)
        #for i in range(len(A)):
        #    children[B[i]]=A[i]
        #return children

        # Method NEW 3
        #A,B = numpy.nonzero(self.__tensor[nodeIndex,:,:])
        #C = numpy.array(A)
        #C[B] = A
        #return list(C)

        # Method NEW 5
        return list(numpy.nonzero(self.__tensor[nodeIndex,:,:].transpose())[1])




    def __eq__(self,other):

        # Comparison of total nodes number
        if self.getNbNodes() != other.getNbNodes():
            return False

        # Comparison of H
        if util.isDiff( self.getH() , other.getH() ):
            return False

        # Comparison of logHMax
        if util.isDiffScalar( self.getLogHMax(), other.getLogHMax() ):
            return False

        # Comparison of the number of nodes of each type
        #if not self.getSummary() == other.getSummary():
        #    return False

        if METICULOUS_COMPARE:
            # Recursive comparison of the structure of the two graphs (Very Expensive !!)
            return Graph.compare(self,0,other,0)
        else:
            # No differences in the phenotype => equality
            return True        

    def getSummary(self):
        # Returns basic informations about the graph
        listVar = []
        listCte = []
        listOp  = []
        # Number of nodes of each type
        for i in range(self.getNbNodes()):
            n = self.__nodes[i]
            v = n.getValue()
            if n.getType() == 'cte':
                listCte.append(v)
            elif n.getType() == 'var':
                listVar.append(v)
            elif n.getType() == 'op':
                listOp.append(v)
        listCte.sort()
        listVar.sort()
        listOp.sort()
        return [listCte, listVar, listOp]



    @classmethod
    def compare(cls,g1,i1,g2,i2):
        # Recursive comparison of node i1 from g1 and i2 from g2
        n1 = g1.__nodes[i1]
        n2 = g2.__nodes[i2]

        # Compare intrinsic node properties
        if not( n1==n2 ):
            return False

        # If intrinsic properties are identical, and if n1 is a leaf, then return TRUE
        if n1.isLeaf():
            return True

        # If not a leaf, compare children
        n1Children = g1.getChildrenIndex(i1)
        n2Children = g2.getChildrenIndex(i2)

        nbArg = n1.getNbArg()
        isSym = cls.__OP_MANAGER.isSymmetric(n1.getValue())
        if isSym:
            # if operator is symetric, we need to consider all combinations of children
            # to see if they're equal
            # ie: we check for each child of n1 if it's equal to a child of n2
            for j1 in range(nbArg):
                findEqual = False
                for j2 in range(len(n2Children)):
                    if Graph.compare(g1,n1Children[j1],g2,n2Children[j2]):
                        findEqual = True
                        break
                if findEqual:
                    # If a match is found between the child of order j2 of n2, we pop the child
                    n2Children.pop(j2)
                else:
                    # Aucune correspondance n'a été trouvé, donc on renvoie false
                    return False
            return True
                    
        else:
            # If operator is not symetric, we compare children 2 by 2
            for j in range(nbArg):
                if not Graph.compare(g1,n1Children[j],g2,n2Children[j]):
                    return False
            return True



    #===========================================#
    #             COMPUTATION OF H              #
    #===========================================#


    def getH(self,nodeIndex=0):
        node = self.__nodes[nodeIndex]
        Graph.__NODE_H_CALL += 1
        if node.isHNone():
            Graph.__NODE_H_CALCULATION += 1
            nodeType = node.getType()
            nodeValue = node.getValue()
            nodeNbArg = node.getNbArg()

            # if node is an operator 
            if nodeType == "op":
                # List of children of the nodes
                children = self.getChildrenIndex(nodeIndex)
                # Construction of the arg list:
                args = []
                for c in children:
                    args.append( self.getH(c) )
                # Calculation of H
                h = self.__OP_MANAGER.computeOperator(nodeValue, nodeNbArg, args )
            # if node is a variable   
            elif nodeType == "var":
                h = self.__VAR_VALUES[nodeValue]
            # if node is a constant
            elif nodeType == "cte":
                #h = numpy.array([nodeValue]*self.__NB_POINTS)
                h = nodeValue

            node.setH(h)

        return node.getH()
            
    def getLogHMax(self,nodeIndex=0):
        n = self.__nodes[nodeIndex]
        if n.isLogHMaxNone():
            h = self.getH(nodeIndex)
            hMax = numpy.amax(abs(h))
            logHMax = abs(numpy.log10(hMax))

            if numpy.isnan(logHMax) or numpy.isinf(logHMax):
                n.setLogHMax(numpy.inf)
                return numpy.inf
            else:
                childrenList = self.getChildrenIndex(nodeIndex)
                for c in childrenList:
                    logHMaxChildren = self.getLogHMax(c)
                    if numpy.isnan(logHMaxChildren) or numpy.isinf(logHMaxChildren):
                        n.setLogHMax(numpy.inf)
                        return numpy.inf
                    if logHMaxChildren > logHMax:
                        logHMax = logHMaxChildren
                n.setLogHMax(logHMax)
                return logHMax
        else:
            return n.getLogHMax()

    #===========================================#
    #    POST-PROCESSING: COMPUTATION OF H     #
    #===========================================#

    def getF(self,nodeIndex=0):
         # Post-Processing
        f = self.__METHOD_POST_PROCESSING(nodeIndex)
        return f

    def postProcessingNone(self,nodeIndex=0):
        return self.getH(nodeIndex)

    def postProcessingScalling(self,nodeIndex=0):
        h = self.getH(nodeIndex)
        [cm,ca] = self.getScallingValues()
        return h*cm+ca

    def postProcessingThreshold(self,nodeIndex=0):
        #TODO: Implement this function
        print "postProcessingThreshold is not implemented yet"
        exit()

    def getScallingValues(self,nodeIndex=0):
        # From the vector h, this method compute the
        # coefficients cm and ca which minimise MSE (cm*h+ca-fRef)

        # Lignes de dénormalisation
        h = numpy.array(self.getH(nodeIndex))   
        # Offset of H:
        hMean = numpy.mean(h)    
        fRefMean = self.__REF_MODEL.getRefFunctionMean()
        FH = numpy.mean(h * self.__REF_MODEL.getRefFunction())
        HH = numpy.mean(h * h)
        hVar = HH-hMean*hMean
        if not util.isDiffScalar(hVar,0):
            cm = 1
        else:
            cm = (FH-hMean*fRefMean)/hVar
        ca = fRefMean-cm*hMean
        return [cm,ca]

    @classmethod
    def setPostProcessing(cls, pp):
        print "Post-Processing: "+pp
        if pp is "none":
            cls.__METHOD_POST_PROCESSING = Graph.postProcessingNone
        elif pp is "scalling":
            cls.__METHOD_POST_PROCESSING = Graph.postProcessingScalling
        elif pp is "threshold":
            cls.__METHOD_POST_PROCESSING = Graph.postProcessingThreshold
        else:
            print "Problem in method \"setPostProcessing\":"
            print pp+" is not recognized.\nThe possible options are: none, scalling, threshold"
            exit()



    #===========================================#
    #           ERROR COMPUTATION               #
    #===========================================#

    def getDiffToRef(self,nodeIndex=0):
        # get f
        f = self.getF(nodeIndex)
        # get fRef
        fRef = Graph.__REF_MODEL.getRefFunction()    
        # Return the abs value of the difference
        return numpy.abs(f-fRef)

    def getRelativeError(self,nodeIndex=0):
        e = self.getDiffToRef(nodeIndex)
        rRef = Graph.__REF_MODEL.getRefFunction()    
        return e/rRef

    def getMaxError(self,nodeIndex=0):
        return numpy.max( self.getDiffToRef(nodeIndex) )

    def getMaxRelativeError(self,nodeIndex=0):
        relError = self.getRelativeError(nodeIndex)
        rRef = Graph.__REF_MODEL.getRefFunction()    
        i = numpy.nonzero(rRef == 0)      
        relError[i] = 0
        return numpy.max( relError )

    def getMeanSquareError(self,nodeIndex=0):
        return numpy.mean(pow( self.getDiffToRef(nodeIndex),2) ) 

    def getMseCheck(self):
        h = self.getH()
        hMean = numpy.mean(h)    
        fRefMean = self.__REF_MODEL.getRefFunctionMean()
        FH = numpy.mean(h * self.__REF_MODEL.getRefFunction())
        HH = numpy.mean(h * h)
        hVar = HH-hMean*hMean
        #if abs(hVar)<util.MACHINE_EPS:
        if not util.isDiffScalar(hVar,0):
            cm = 1
        else:
            cm = (FH-hMean*fRefMean)/hVar
        ca = fRefMean-cm*hMean
        f = cm*h+ca
        fRef = Graph.__REF_MODEL.getRefFunction() 
        error = numpy.abs(f-fRef)
        mse = numpy.mean( pow(error,2) ) 
        return mse


    def getCorrelationError(self,nodeIndex=0):
        return 1-self.getCorrelation(nodeIndex)

    def getCorrelation(self,nodeIndex=0):
        node = self.__nodes[nodeIndex]
        nodeType = node.getType()
        if nodeType == 'cte':
            # if it's a constant, we consider that correlation is null.
            nodeCorrelation = 0.0

        elif nodeType == 'var':
            # If a variable, we get the correlation in ref model
            # (Correlation between y and each input is computed once and for all at load time)
            # TODO: this is not necessary 
            nodeCorrelation = self.__VAR_COR[node.getValue()]

        elif nodeType == "op":
            # If node is operator, compute correlation depending on H
            h = self.getH(nodeIndex)
            hStd  = numpy.std( h )
            if numpy.any(numpy.isinf(h)) or numpy.any(numpy.isnan(h)) or numpy.isinf(hStd) or self.isConstant(nodeIndex):
                # if the node has inf or Nan or has infinite std, or is constant
                nodeCorrelation = 0.0
            else:
                # Pearson correlation:
                # Center H
                hCenter = h-numpy.mean(h)
                hCenter /= hStd
                # Compute correlation
                nodeCorrelation = numpy.mean( hCenter * self.__REF_FUNC ) 
                # Compute std of H
                nodeCorrelation /= self.__REF_FUNC_STD
                # Keep abs value
                nodeCorrelation = abs(nodeCorrelation)
                # Check for non valid correlations
                if (nodeCorrelation > 1.0) or (nodeCorrelation < 0.0):
                    nodeCorrelation = 0.0
        return nodeCorrelation



    @classmethod
    def setErrorMethod(cls, errorString):
        print "Error calculation method: "+errorString
        fRef = cls.__REF_MODEL.getRefFunction()
        fRefMin = numpy.amin(fRef)
        fRefMax = numpy.amax(fRef)
        if errorString is "mse":
            cls.__METHOD_OBJECTIVE_ERROR = Graph.getMeanSquareError
            we = numpy.mean(pow(fRef,2))
        elif errorString is "max":
            cls.__METHOD_OBJECTIVE_ERROR = Graph.getMaxError
            we =  fRefMax-fRefMin
            if we<1:
                we=1
        elif errorString is "correlation":
            cls.__METHOD_OBJECTIVE_ERROR = Graph.getCorrelationError
            we = 1
        elif errorString is "relative":
            cls.__METHOD_OBJECTIVE_ERROR = Graph.getMaxRelativeError
            fRefAbsMin = numpy.amin(abs(fRef))
            we = fRefAbsMin/(fRefMax-fRefMin)
        else:
            print "Problem in method \"setError\":"
            print "The possible options are: mse, max, correlation, relative"
            exit()
        cls.__WORSE_ERROR = we
        print "Worse possible error: "+str(we) 

    def getError(self,nodeIndex=0):
        node = self.__nodes[nodeIndex]
        if node.isErrorNone():
            nodeType = node.getType()
            if nodeType == 'cte' or nodeType == 'var':
                # Medium penalisation
                e = Graph.__WORSE_ERROR * 4
            elif nodeType == "op":
                # If the node is an operator, we 
                logHMax = self.getLogHMax(nodeIndex)
                if numpy.isinf(logHMax) or numpy.isnan(logHMax):
                    # graphs with nan or inf are penalized, but less than constant or var nodes.
                    # The reason is that the complexity in these nodes is interresting.
                    e = Graph.__WORSE_ERROR * 1
                elif self.isConstant(nodeIndex):
                    # Penalization of constant nodes
                    e = Graph.__WORSE_ERROR * 3
                elif logHMax > LOG_H_LIMIT:
                    # If h is too large, the calculation of the error is not reliable. 
                    e = Graph.__WORSE_ERROR * (1+logHMax-LOG_H_LIMIT)
                    #print "in getError, fAbsMax: "+str(hMax)
                    #print "                      penalty: "+str(penaltyCoef)
                else:
                    # Otherwise, we compute the Error
                    e = self.__METHOD_OBJECTIVE_ERROR(nodeIndex)

            # Record this value in the node
            node.setError(e)

        return node.getError()

    #===========================================#
    #        COMPLEXITY COMPUTATION             #
    #===========================================#

    def getComplexity(self):
        if self.isConstant():
            # Constant graph are penalized in complexity. 
            return float('inf')
        else:
            return self.getNbNodes()+3*self.getNbUnusedVariables() #+self.__graph.getNbLinks()

    def getListUsedVariables(self):
        nb = self.getNbNodes()
        nbv = self.getNbVariables()
        tabUsedVariables = numpy.zeros( [nbv] , dtype=bool )
        for i in range(nb):
            if self.__nodes[i].getType()=="var":
                k = self.__nodes[i].getValue()
                tabUsedVariables[k] = True
        tabUsedVariables = numpy.nonzero(tabUsedVariables)[0]
        return tabUsedVariables

    def getNbUsedVariables(self):
        return len(self.getListUsedVariables())

    def getNbUnusedVariables(self):
        return self.getNbVariables()-len(self.getListUsedVariables())

    #=========================#
    #                         #
    #  Criteria of all nodes  #
    #                         #
    #=========================#

    def getNodeCriteriaList(self):
        # Error value for each node. The smaller the better.
        criteriaList = []
        for i in range(self.getNbNodes()):
            criteria = self.getError(i)
            criteriaList.append(criteria)
        return criteriaList


    # ============================= #
    #     Print & Display           #
    # ============================= #


    # Return a string containing the expression of graph as text
    def getString(self,nodeIndex=0):
        node = self.__nodes[nodeIndex]
        if node.getType() == "op": 
            nodeValue = node.getValue()
            nodeNbArg = node.getNbArg()
            # Construct the string of each arguments
            args = []            
            for c in self.getChildrenIndex(nodeIndex):
                args.append( self.getString(c) )
            # Get the String of the operator
            s = self.__OP_MANAGER.getString(nodeValue,nodeNbArg)
            # Put arg's string into op's string
            for i in range(nodeNbArg):
                s= s.replace("$x"+str(i)+"$",args[i])
        else:
            s = node.getString()

        return s


    def printLinks(self):
        # Print all the links between nodes.
        # Not very fancy, but it's the basic display mode.
        nb = self.getNbNodes()
        print "#========================================================"
        print "# Nodes Number: "+str(nb)
        if self.__nodes[0].isHNone():
            hStatus = 'h = NONE'
        else:
            nH = str(self.getH(0))  
            if len(nH)>20:
                nH = nH[0:20]  
            hStatus = 'h = '+nH

        print "# n0: "+hStatus
        for i in range(nb):
            iValue = self.__nodes[i].getString()
            iType =  self.__nodes[i].getType()
            iNodeStr = "n"+str(i)
            while len(iNodeStr)<4:
                iNodeStr+=" "
            iNodeStr+="("+iType+" "+iValue+")--"
            while len(iNodeStr)<18:
                iNodeStr+= '-'

            for k in range(self.__nodes[i].getNbArg()):
                for j in range(nb):
                    if self.__tensor[i,j,k]:
                        # Node Infos
                        jType =  self.__nodes[j].getType()
                        jValue = self.__nodes[j].getString()
                        if jType=='cte':
                            jValue=jValue[0:7]
                        elif jType=='op':
                            jType+=' '
                        # Node name
                        jNodeStr = "n" +str(j)
                        while len(jNodeStr)<4:
                            jNodeStr+=" "
                        jNodeStr+="("+jType+" "+jValue
                        # Node Value
                        while len(jNodeStr)<17:
                            jNodeStr+=" "            
                        # Node status
                        if self.__nodes[j].isHNone():
                            hStatus = 'h = NONE'
                        else:
                            nH = str(self.getH(j))  
                            if len(nH)>20:
                                nH = nH[0:20]  
                            hStatus = 'h = '+nH
                        jNodeStr+=') '+hStatus           
                        print "# "+iNodeStr+str(k)+"--> "+jNodeStr
                        # Update iNodeStr so that the father's name is not repeated.
                        iNodeStr = ' '*len(iNodeStr)

        if nb==1: 
            iValue = self.__nodes[0].getString()
            iType =  self.__nodes[0].getType()
            print "# n0 ("+iType+" "+iValue+")"
        print "#========================================================"



    def getDot(self):
        # The Graph file is composed of
        # - A header
        # - List of Op Nodes
        # - List of Cte Nodes
        # - List of Var Nodes
        # - List of links

        tabOp = []
        tabOp.append("/* Operator nodes */\n")
        tabOp.append("node[margin=\"0\",shape=\"circle\",style=\"filled\",fillcolor=\"white\",penwidth=\"1.0\"]\n")

        tabCte = []
        tabCte.append("/* Constant nodes */\n")
        tabCte.append("node[margin=\"0\",shape=\"rectangle\",style=\"filled\",fillcolor=\"grey90\",penwidth=\"1.0\"]\n")

        tabVar = []
        tabVar.append("/* Operator nodes */\n")
        tabVar.append("node[margin=\"0\",shape=\"square\",style=\"filled\",fillcolor=\"grey90\",penwidth=\"2.0\"]\n")

        tabLinks = []
        tabLinks.append("/* Links */\n")

        # Write the list of nodes:
        for i in range(self.getNbNodes()):
            # Info on the node
            n = self.__nodes[i]
            iType   = n.getType()
            iValue   = n.getValue()
            iString = n.getString()
            iNbArg = n.getNbArg()
            s = "  n"+str(i)+" [label=\"n"+str(i)+"\\n"+iString+"\"];\n" 
            if iType == "op":
                tabOp.append(s)
            elif iType == "var":
                tabVar.append(s)
            elif iType == "cte":
                tabCte.append(s)    

            #Links
            children = self.getChildrenIndex(i)
            for k in range(len(children)):
                j = children[k]
                # Write the connection
                s = "  n"+str(i)+" -> n"+str(j)
                # If necessary, write the child number
                if (not self.__OP_MANAGER.isSymmetric(iValue)) and (iNbArg>1):
                    s+= " [taillabel=\""+str(k)+"\"]"
                s+="\n"
                tabLinks.append(s)

        # Concatenation
        tab = []
        tab.append("digraph {\n")
        tab.append("margin=\"0\"\n") 
        tab.extend(tabOp)
        tab.extend(tabCte)
        tab.extend(tabVar)            
        tab.extend(tabLinks)
        tab.append("}") 

        return tab


    def getOperatorsList(self):
        self.printLinks()

        # Gather the operators present in the graph
        opList = list()
        for n in self.__nodes:
            if n.getType()=='op':
                opList.append([n.getValue() , n.getNbArg()])

        # Uniquify opList
        opListUnique = []
        for op in opList:
            if not op in opListUnique:
                opListUnique.append(op)
        opList = opListUnique

        for i in range(len(opList)):
            op = opList[i]
            s = op[0] 
            while len(s)<10:
                s += " "
            s+="; "+str(op[1])+" "
            ostr = self.__OP_MANAGER.getOriginalString(op[0])
            if len(ostr):
                s+="; \""+ostr+"\""
            opList[i] = s

        return opList


    def writeDot(self, fileName="Graph" ):
        # DEBUG
        tab = self.getDot()
        fid = open(fileName+".dot", 'w')
        for e in tab:
            fid.write(e)
        fid.close()

    def writeAlgo(self, fileName="Graph" ):
        # DEBUG
        tab = self.getAlgo()
        fid = open(fileName+".algo", 'w')
        for e in tab:
            fid.write(e+"\n")
        fid.close()


    def display(self, fileName="Graph" ):
        self.writeDot(fileName)
        # Compilation du fichier dot
        os.system("dot -Tpdf "+fileName+".dot -o "+fileName+".pdf &")
        os.system("display "+fileName+".pdf &")

    def getNbParents(self,i):
        return numpy.count_nonzero(self.__tensor[:,i,:])



    def getAlgoOperator(self,nodeIndex,tabHasItsOwnLine):
        # Construction of the strings of all arguments of this node
        children = self.getChildrenIndex(nodeIndex)
        args = []            
        for c in children:
            childrenType = self.__nodes[c].getType()
            if childrenType=="cte":
                cStr = "c"+str(c) 
            elif childrenType=="var":
                childrenValue = self.__nodes[c].getValue()
                cStr = "x"+str(childrenValue) 
            elif tabHasItsOwnLine[c]:
                # If children node "c" has its own line, then 
                # the expression of the node will just be its name
                cStr = "h"+str(c)        
            else:
                # Otherwise, the expression has to be recursively built
                # Which means that what is returned is not the child's name 
                # but the FULL expression of the child.
                cStr = self.getAlgoOperator(c,tabHasItsOwnLine)
            args.append(cStr)
            
        # Get some basic information on the node
        node = self.__nodes[nodeIndex]
        nodeValue = node.getValue()
        nodeNbArg = node.getNbArg()

        # The expression of the current operator node is build        
        s = self.__OP_MANAGER.getString(nodeValue,nodeNbArg)
        for i in range(nodeNbArg):
            s= s.replace("$x"+str(i)+"$",args[i])
        return s

    def setHasItsOwnLine(self,i,tab,distance,distanceMax):
        # tab is tabHasItsOwnLine
        if distance==distanceMax and self.__nodes[i].getType()=="op":
            tab[i]=True;
        if tab[i]:
            distance = 0;
        for c in self.getChildrenIndex(i):
            tab = self.setHasItsOwnLine(c,tab,distance+1,distanceMax)
        return tab

    def getAlgo(self):
        # Order nodes by depth
        depthList = self.getDepthList()
        d = []
        for i in range(self.getNbNodes()):
            d.append([i,depthList[i]])
        d.sort(cmp=lambda x,y: cmp(x[1], y[1]))

        nb = self.getNbNodes()
        # Creation of the boolean array tabHasItsOwnLine
        tabHasItsOwnLine = numpy.zeros( [nb] , dtype=bool )
        # To have its own line, the node must be an operator AND
        # - Be an operator used several times
        #  (in that case, having its own line allows to compute its result only once)
        # - Or be the root  
        for i in range(nb):
            bool1 = self.__nodes[i].getType()=='op'
            nbParents = self.getNbParents(i)
            bool2 = (nbParents==0) 
            bool3 = (nbParents>=2)
            tabHasItsOwnLine[i] = bool1 and (bool2 or bool3)
        # But there is an additional limitation : 
        # The vertical distance between to nodes that have their own lines 
        # must be smaller than 32. In other words, it is not allowed to have more than 32
        # nested operators on the same line.
        distanceMax = 10;
        tabHasItsOwnLine = self.setHasItsOwnLine(0,tabHasItsOwnLine,1,distanceMax)



        # Construction of nodes expression for the constant node and for
        # the operator nodes which has their own line
        tabC = []
        tabOp = []
        for e in d[::-1]:
            i = e[0] # Node index
            iType = self.__nodes[i].getType()
            if iType=='cte':
                # All constants have their own line
                tabC.append( "c"+str(i)+" = "+str(self.__nodes[i].getValue()) )
            elif tabHasItsOwnLine[i]:
                # For operator node, we have to check if it has its own line
                s = self.getAlgoOperator(i,tabHasItsOwnLine)
                s = util.removeParenthesis(s)
                tabOp.append( "h"+str(i)+" = "+s )

        # Concatenation des lignes d'opération et de déclaration de constantes
        tabC.extend(tabOp)
        
        # Scalling
        lastLine = "f = h0"
        [cm,ca] = self.getScallingValues() 
        # Write the multiplicative constant, if needed
        if not str(cm)=='1.0':
            tabC.append("cm = "+str(cm))
            lastLine += "*cm"
        # Write the additive constant, if needed
        if not str(ca)=='0.0':
            tabC.append("ca = "+str(ca))
            lastLine += " + ca"
        tabC.append(lastLine)

        return tabC


    def getStructureString(self):
        # Structure of the graph (to write it in the Ind file)
        nb = self.getNbNodes()
        tab = []
        for i in range(nb):
            node = self.__nodes[i]
            nodeType =  node.getType()
            nodeStr = node.getString()

            # Node description
            tab.append("node "+str(i)+" "+nodeType+" "+nodeStr)

            # Links description
            children = self.getChildrenIndex(i)
            for k in range(len(children)):
                tab.append(str(i)+" "+str(children[k])+" "+str(k))

        return tab


    # ============================== #
    #                                #
    #   GENETIC OPERATOR MANAGEMENT  #
    #                                #
    # ============================== #

    def callMutation(self,i):

        mutationName = Graph.getMutationName(i)

        if PRINT:
            print "call of the mutation: "+mutationName

        if mutationName is not None:
            exec("self."+mutationName+"()")
        else:
            print "non existing mutation: "+str(mutationName)
            util.quit(__file__)

        if CHECK:
            self.checkConsistency(mutationName)

    @classmethod
    def getMutationName(cls,i):
        if   i==0:
            return "mutationInternCrossover"
        elif i==1:
            return "mutationLeaf2Leaf"
        elif i==2:
            return "mutationOp2Op"
        elif i==3:
            return "mutationLeaf2Op"
        elif i==4:
            return "mutationOp2Leaf"
        elif i==5:
            return "mutationShortenGraph"
        elif i==6:
            return "mutationCreateLink"
        elif i==7: 
            return "mutationKeepBest"
        elif i==8: 
            return "mutationConstants"
        else:
            return None


    #===================================================#
    #              GENETIC OPERATORS                    #
    #===================================================#

    def mutationInternCrossover(self):

        # Usefull matrix #
        nb = self.getNbNodes()
        isLeafVector = self.getIsLeafVector()
        hasCousinsVector = self.getHasCousinsVector()
        cousinsMatrix = self.getCousinsMatrix()

        # Choice of S #
        # To be eligible for the "S position", a node must:
        # 1 - have children
        # 2 - have cousins
        # Good nodes (low criteria) will be privileged           
        eligible = numpy.logical_not(isLeafVector) * hasCousinsVector
        nodeCriteriaList = self.getNodeCriteriaList() 
        if not (numpy.any(eligible)):
            # Pour éviter certaines boucles infinies, et pour créer un peu de diversité,
            # Si la mutation n'est pas possible, on fait juste un "Bloom".
            self.mutationLeaf2Op()
            return
        s = util.indexChoice(eligible,nodeCriteriaList,"low") # OK

        # Choice of W #
        # w is chosen among the cousins of s
        eligible = cousinsMatrix[s,:]
        w = util.indexChoice(eligible,nodeCriteriaList,"high") # OK

        # Concatenation #
        newGraph = Graph.concatenate(self,self)
        self.__nodes = newGraph.__nodes
        self.__tensor = newGraph.__tensor

        # Modification of the link to s #
        self.__tensor[:,s+nb,:] = self.__tensor[:,w,:] 
        self.__tensor[:,w,:] = False

        # Reset of nodes #
        # Mise à None des H de tous les noeuds qui 
        # sont des ancêtres de la copie de s
        self.resetAncestors(s+nb)

        # Reuse rule #
        pile = [s]
        while len(pile):
            i = pile.pop(0)

            # Reusability:
            D = self.getDescendantsMatrix()
            arg1 = D[s+nb,i+nb] or (s==i)
            arg2 = numpy.logical_not( D[i,s+nb] )
            arg3 = D[0,i]
            reuse = arg1 and arg2 and arg3

            # Test statistique
            if reuse:
                r = random.random()
                reuse = (r < 1./2.)

            if reuse:
                # Les liens vers i' sont redirigés vers i
                self.__tensor[:,i,:] += self.__tensor[:,i+nb,:]
                self.__tensor[:,i+nb,:] = False
            else:
                # Si i n'est pas réutilisé, alors on va voir 
                # si les enfants de i doivent l'être.
                children = self.getChildrenIndex(i)
                if children is not None:
                    pile.extend( children )

        # Delete Useless Nodes #
        self.deleteUselessNodes()





    def mutationLeaf2Leaf(self):
        # We pick a node with a poor criteria
        i = util.indexChoice( self.getIsLeafVector() , self.getNodeCriteriaList() , "high" ) #  OK
        # Replace it with a random leaf
        self.__nodes[i] = Node.buildRandomLeaf(range(self.getNbVariables()))
        # Reset all ancestors
        self.resetAncestors(i)


    def mutationOp2Op(self):
        # list nodes that are not leafs
        eligible = numpy.logical_not(self.getIsLeafVector()) 
        # If no eligible nodes, return.
        if not numpy.any(eligible):
            self.mutationLeaf2Op()
            return
        # Pick a node with poor criteria
        i = util.indexChoice( eligible , self.getNodeCriteriaList() , "high" ) # OK
        # Gather info
        n = self.__nodes[i] 
        nNbArg = n.getNbArg()
        nOp = n.getValue()

        # Compute list of eligible operators for this leaf
        # (i.e. same nbArgs)
        listEligibleOp = self.__OP_MANAGER.getListOp(nNbArg)
        # Remove current operator
        listEligibleOp.remove(nOp)
        # Check it's not empty
        if not len(listEligibleOp):
            self.mutationLeaf2Op()
            return
        
        # Choice of the new value among the op of same nbArg
        n.setOp(random.choice(listEligibleOp))
        # Nullification of the node
        n.resetH()
        # Nullification of all its ancestors
        self.resetAncestors(i)

    def mutationLeaf2Op(self):
        nb = self.getNbNodes()
        # pick a leaf uniformly
        i = util.indexChoice( self.getIsLeafVector()  )
        # Replace leaf by operator
        self.__nodes[i] = Node.buildRandomOp( self.__OP_MANAGER  )
        # create children of node "i"
        for na in range(self.__nodes[i].getNbArg()):
            self.addNode( Node.buildRandomLeaf(range(self.getNbVariables())) )
            self.__tensor[i,nb+na,na] = True

        # Reset all ancestors
        self.resetAncestors(nb)

    def mutationOp2Leaf(self):
        if PRINT:
            print "BEGIN mutationOp2Leaf "
            self.printLinks()
        # list non-leaf nodes
        eligible = numpy.logical_not(self.getIsLeafVector()) 
        # if no node is eligible, just apply a minor mutation
        if not numpy.any(eligible):
            self.mutationLeaf2Op()
            return
        # pick a node among those with high criteria
        i = util.indexChoice( eligible , self.getNodeCriteriaList() , "high" ) 
        # The node is replaced by a Leaf
        self.__nodes[i] = Node.buildRandomLeaf(range(self.getNbVariables()))
        if PRINT:
            print "mutationOp2Leaf: node "+str(i)+" "+str(self.__nodes[i].getValue())
        # And all links from i to other nodes are deleted
        self.__tensor[i,:,:] = False
        # Reset all ancestors of i
        self.resetAncestors(i)
        # Delete un-used nodes
        self.deleteUselessNodes()



    def mutationShortenGraph(self):
        WRITE_DOT = False

        if PRINT:
            print "Begin Shorten"
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase0")
            self.writeAlgo("mutationShortenGraph_Phase0")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Debut")
        if PRINT:
            print "\nBEGIN Phase 1: Replacement of Nan and Inf by a Leaf Node"
        modificationCounter = 0
        # If a node's H is Nan or Inf, replace the node by a random leaf.
        for i in range(self.getNbNodes()):
            # if the node is an operator
            if self.__nodes[i].getType() == "op":
                h = self.getH(i)
                if numpy.any(numpy.isinf(h)) or numpy.any(numpy.isnan(h)):
                    # The node is replaced by a Leaf
                    self.__nodes[i] = Node.buildRandomLeaf(range(self.getNbVariables()))
                    # And all links from i to other nodes are deleted
                    self.__tensor[i,:,:] = False
                    self.resetAncestors(i)
                    modificationCounter += 1
        self.deleteUselessNodes()

        if PRINT:
            print "END phase 1. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase1")
            self.writeAlgo("mutationShortenGraph_Phase1")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 1")
        if PRINT:
            print "\nBEGIN Phase 2: replacement of nodes with constant H by a constant leaf node"


        # If a node's H is constant, replace the node by this constant.
        modificationCounter = 0
        for i in range(self.getNbNodes()):
            # if the node is an operator
            if self.__nodes[i].getType() == "op":
                # and if the node H is constant,
                if self.isConstant(i):
                    h = self.getH(i)
                    if self.isScalar(i):
                        v = h
                    else:
                        v = h[0]
                    # then the node is changed into a constant one
                    self.__nodes[i].reset('cte',v)
                    # And all links from i to other nodes are deleted
                    self.__tensor[i,:,:] = False
                    # The H of the node can have been slightly modified
                    self.resetAncestors(i)
                    modificationCounter += 1
        self.deleteUselessNodes()

        if PRINT:
            print "END phase 2. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase2")
            self.writeAlgo("mutationShortenGraph_Phase2")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 2")
        if PRINT:
            print "\nBEGIN Phase 3: Merging the variable nodes."

        # Merging all variables
        # All nodes "x1" are merged and all links pointing to any "x1" node are 
        # now pointing to ONE single "x1" nodes.
        modificationCounter = 0
        for nv in range(self.getNbVariables()):
            targetNode = None
            for i in range(self.getNbNodes()):
                if (self.__nodes[i].getType()=="var") and (self.__nodes[i].getValue()==nv):
                    if targetNode is None:
                        # This node will be used each time that this variable occurs
                        targetNode = i
                    else:
                        # If targetNode is already defined, then all connection to "i"
                        # are re-routed to targetNode
                        self.__tensor[:,targetNode,:] += self.__tensor[:,i,:]
                        # The connections to i are deleted
                        self.__tensor[:,i,:] = False
                        modificationCounter += 1
        self.deleteUselessNodes()

        if PRINT:
            print "END phase 3. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase3")
            self.writeAlgo("mutationShortenGraph_Phase3")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 3")
        if PRINT:
            print "\nBEGIN Phase 4: Bypass the nodes that does not change H"

        # If a operator node "i" has a H which is equal to one of its argument's node "j",
        # then "i" is removed and all link to "i" are re-routed to "j"
        # look into the contents of graph:
        modificationCounter = 0
        for i in range(self.getNbNodes()):
            # if the node is an operator
            if self.__nodes[i].getType() == "op":
                # We get the H and the list of children
                h = self.getH(i)
                children = self.getChildrenIndex(i)
                delete = False
                # If for ONE of the children "j"...
                for j in children:
                    # ... the H of "i" and "j" are the same ...
                    if not util.isDiff(h,self.getH(j)):
                        # ... then we delete the node "i"
                        delete=True
                        break
                if delete:
                    if PRINT:
                        print "All links to "+str(i)+" are re-routed to "+str(j)
                    # To delete "i", all links to "i" are re-routed to "j"
                    self.__tensor[:,j,:] += self.__tensor[:,i,:]
                    self.__tensor[:,i,:] = False
                    self.resetAncestors(j)
                    modificationCounter += 1
        self.deleteUselessNodes()

        if PRINT:
            print "END phase 4. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase4")
            self.writeAlgo("mutationShortenGraph_Phase4")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 4")
        if PRINT:
            print "\nBEGIN Phase 5: Merge constant arguments of n-ary symetric operators"

        # Merge of arguments
        # If a node has 3 children or more
        # AND, the node is a symmetric operator
        # AND, If several of the children are constants,
        # THEN, the constant nodes are merged
        modificationCounter = 0
        for i in range(self.getNbNodes()):
            # if the node is an operator with 3 arguments or more
            if self.__nodes[i].getNbArg() >= 3:
                op = self.__nodes[i].getValue()
                if self.__OP_MANAGER.isSymmetric(op):
                    children = self.getChildrenIndex(i)
                    # Filter the children
                    cList = [] # List of constant children (contains a list of nodes)
                    cArgs = [] # List of constant arguments (contains a list of numeric array)
                    vList = [] # List of non-constant children (contains a list of nodes)
                    for c in children:
                        if self.__nodes[c].getType()=="cte":
                            cList.append(c)
                            cArgs.append(self.getH(c))
                        else:
                            vList.append(c)
                    nc = len(cList)
                    nv = len(vList)
                    # If there are 2 constant children or more ...
                    if nc >= 2:
                        # A new node is created to replace them
                        newCte = self.__OP_MANAGER.computeOperator(op,nc,cArgs)
                        newNode = Node('cte',newCte,0)
                        # Addition of the node to the graph
                        self.addNode(newNode)
                        # Calculation of the index of this node
                        j = self.getNbNodes()-1
                        # The nbArg of "i" is changed:
                        self.__nodes[i].setNbArg(nv+1)
                        # The connections from "i" are reset
                        self.__tensor[i,:,:] = False
                        # The non-constant children are changed to be the first arguments
                        for v in range(nv):
                            self.__tensor[i,vList[v],v] = True
                        # then "i" is linked to "j"
                        self.__tensor[i,j,nv] = True
                        if nv == 0:
                            # If the operator only points to constants (it can happen, though rarely)
                            # Then node "j" takes the place of node "i"
                            self.__tensor[:,j,:] = self.__tensor[:,i,:]
                            self.__tensor[:,i,:] = False
                        modificationCounter += 1
                        self.resetAncestors(j)
        self.deleteUselessNodes()



        if PRINT:
            print "END phase 5. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase5")
            self.writeAlgo("mutationShortenGraph_Phase5")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 5")
        if PRINT:
            print "\nBEGIN Phase 6: Merge the similar branches"

        # Merge of similar branches
        # If two nodes are recursively similar (ie: their complete branches are equal)
        # Then they are merged
        modificationCounter = 0
        n = self.getNbNodes()
        CousinsMatrix = self.getCousinsMatrix()
        for i in range(n):
            # List nodes of index > i and that are cousins of i
            jList = i+1+numpy.flatnonzero(CousinsMatrix[i,i+1:n])
            for j in jList:
                if Graph.compare(self,i,self,j):
                    # j is nobody's cousins in the matrix. That allow him not be be considered again in the next iterations.
                    CousinsMatrix[:,j] = False
                    CousinsMatrix[j,:] = False
                    # Links to j are rerouted to i
                    self.__tensor[:,i,:] += self.__tensor[:,j,:]
                    self.__tensor[:,j,:] = False
                    modificationCounter += 1
        self.deleteUselessNodes()



        if PRINT:
            print "END phase 6. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase6")
            self.writeAlgo("mutationShortenGraph_Phase6")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 6")
        if PRINT:
            print "\nBEGIN Phase 7: Merge the sym operators"


        # Merge of sym operators
        # Replace a+(b+c) by a+b+c
        # or min(a,min(b,c)) by min(a,b,c)
        modificationCounter = 0
        change = True
        while change:
            change = False
            for i in range(self.getNbNodes()):
                # if the node is a symetric operator
                p = self.__nodes[i] # Parent
                op = p.getValue()
                iNbArg = p.getNbArg()

                if self.__OP_MANAGER.isSymmetric(op):
                    children = self.getChildrenIndex(i)
                    # if one of the children is the same operator and has only one parent
                    for k in range(len(children)):
                        j = children[k] # index of the child
                        c = self.__nodes[j] # child
                        if c.getType()=="op" and c.getValue()==op and self.getNbParents(j)==1:
                            jNbArg = c.getNbArg()
                            # If the operator can have a nbArg big enough
                            if self.__OP_MANAGER.exists(op,iNbArg+jNbArg-1):
                                # Fusion of i and j
                                if PRINT:
                                    print "Fusion of "+str(i)+" and "+str(j) 
                                modificationCounter += 1
                                # j is not the k-th child of i anymore
                                self.__tensor[i,j,k] = False                    
                                # Small children
                                children2 = self.getChildrenIndex(j)
                                for k2 in range(len(children2)):
                                    j2 = children2[k2]
                                    if k2==0:
                                        # j2 takes the place of j 
                                        self.__tensor[i,j2,k] = True
                                    else:
                                        # j2 is add to the nodes
                                        self.__tensor[i,j2,iNbArg-1+k2] = True
                                p.setNbArg(iNbArg+jNbArg-1)
                                self.resetBranch(i)
                                change = True
                                break # Continue the loop but with another parent.

        self.deleteUselessNodes()

        if PRINT:
            print "END phase 7. Number of modifications: "+str(modificationCounter)
            self.printLinks()
        if WRITE_DOT:
            self.writeDot("mutationShortenGraph_Phase7")
            self.writeAlgo("mutationShortenGraph_Phase7")
        if CHECK:
            self.checkConsistency("mutationShortenGraph - Phase 7")









    def mutationCreateLink(self):
        # Replace node "w" with a link to node "s"

        # Eligible "s" nodes must have cousins
        HC = self.getHasCousinsVector()
        # If no node has cousins, we can not proceed. Just apply minor mutation.
        if not numpy.any(HC):
            self.mutationLeaf2Op()
            return

        # Pick a node "s" among eligible nodes, favoring good nodes (low criteria)
        s = util.indexChoice( HC , self.getNodeCriteriaList() , "low" ) 

        # Eligible "w" nodes must be cousins of "s"
        C = self.getCousinsMatrix()
        # Among eligible nodes, pick "w" favoring bad nodes (high criteria)
        w = util.indexChoice( C[s,:] , self.getNodeCriteriaList() , "high" ) #OK

        # As "w" will be replaced by "s", we must reset its ancestors.
        self.resetAncestors(w)
        
        # Links toward "w" are re-routed to "s"
        self.__tensor[:,s,:] += self.__tensor[:,w,:]
        self.__tensor[:,w,:] = False

        # Delete useless nodes
        self.deleteUselessNodes()


    def mutationKeepBest(self):
        # Pick node with best correlation and remove everything not below it.
        i = self.getBestNodeIndex()
        if i==0:
            # if root, do nothing
            return
        else:
            # Move "i" to root
            self.__nodes[0] = self.__nodes[i]
            # Copy in "0" the links of "i"
            self.__tensor[0,:,:] = self.__tensor[i,:,:]
            # Cut all links to "i"
            self.__tensor[:,i,:] = False
            # Remove useless
            self.deleteUselessNodes()

    def mutationConstants(self):
        nb = self.getNbNodes()
        eligible = numpy.zeros(nb,dtype=bool)
        # list all nodes of type "cte"
        for i in range(nb):
            eligible[i] = (self.__nodes[i].getType()=="cte")
        # if none, then return
        if not numpy.any(eligible):
            self.mutationLeaf2Op()
            return
        # Pick one randomly
        i = util.indexChoice(eligible)
        # save constant and error value
        n = self.__nodes[i]
        v0 = n.getValue()
        e0 = self.getError()
        # Change constant
        if random.random() < 0.5:
            v1 = v0 * (1.0+e0*util.symmetricExp())
        else:
            v1 = v0 + util.symmetricExp()            
        n.setCte(v1)
        # Reset ancestors
        self.resetAncestors(i)
        
        # Optimization
        e2 = 0
        while e2<e0:
            # Pick a node to modify
            i = util.indexChoice(eligible)
            n = self.__nodes[i]
            # Save value and error
            v0 = n.getValue()
            e0 = self.getError()
            # Change constant
            v1 = v0 + random.gauss(0,abs(v0)/5) * e0 / Graph.__WORSE_ERROR
            n.setCte(v1)
            self.resetAncestors(i)
            # Compute new error
            e1 = self.getError()
            # if diff between e0 and e1 is large enough, follow slope
            if util.isDiffScalar(e1,e0):
                # Compute new constant
                v2 = v0 - 0.5*e0*(v1-v0)/(e1-e0)
                # Set constant
                n.setCte(v2)
                # Reset parents
                self.resetAncestors(i)
                # Compute new error
                e2 = self.getError()
            else:
                # Otherwise, we quit
                return                 

    @classmethod            
    def externalCrossover(cls,g1,g2):
        n1 = g1.getNbNodes()
        n2 = g2.getNbNodes()
        gn = Graph.concatenate(g1,g2)
    
        # Choice of "w" in g1:
        eligible = numpy.ones(n1,dtype=bool)
        w = util.indexChoice(eligible,g1.getNodeCriteriaList(),"high") # OK

        # Choice of "s" in g2:
        # "s" must not be a leaf
        eligible = numpy.logical_not (g2.getIsLeafVector())
        # If g2 has only leafs, ie g2 has only one node, then this only node is chosen
        if not numpy.any(eligible):
            s = 0
        else:
            s = util.indexChoice(eligible,g2.getNodeCriteriaList(),"low") # OK
        # as "s" is in g2, its index is augmented so that 
        # s is in [n1,n1+n2-1]
        s += n1

        # Links to "w" are re-routed to "s"
        gn.__tensor[:,s,:] = gn.__tensor[:,w,:]
        gn.__tensor[:,w,:] = False        

        # Reset ancestors
        gn.resetAncestors(s)

        # Remove useless
        gn.deleteUselessNodes()

        if CHECK:
            gn.checkConsistency('Graph.externalCrossover')

        return gn




    @classmethod
    def linearCrossover(cls,graphList):

        nbGraphs = len(graphList)
        if nbGraphs < 2:
            print "Not enough graphs to perform linear crossover"

        # Build matrix containing all signals
        R = numpy.ones([Graph.__REF_MODEL.getNbPoints(),nbGraphs+1])   
        for k in range(nbGraphs):
            R[:,k+1] = graphList[k].getH()
        # Solve system
        coefList = numpy.linalg.lstsq(R,Graph.__REF_MODEL.getRefFunction())[0]
        # Remove coef of constant vector
        coefList = list(coefList)[1:nbGraphs+1]

        if PRINT:
            print "\n\n  SUPER IND\n  Coefs are: "
            for c in coefList:
              print "     "+str(c)

        # Construct base
        g = graphList.pop(0)
        coef = coefList.pop(0)

        # Build a small graph for connection
        gs = Graph();
        gs.addNode(Node('op','*',2))
        gs.addNode(Node('cte',coef,0))
        gs.__tensor[0,1,0] = True # NodeCte is the first son of Node*  

        # Connecting
        gn = Graph.concatenate(gs,g)
        gn.__tensor[0,2,1] = True # The root of g is the 2nd son of Node*

        for k in range(len(graphList)):
            # Creation of a small graph for connection
            gs = Graph();
            gs.addNode(Node('op','+',2))
            gs.addNode(Node('op','*',2))
            gs.addNode(Node('cte',coefList[k],0))
            gs.__tensor[0,1,1] = True; # Node* is the 2nd son of Node+ (the 1st will be gn)
            gs.__tensor[1,2,0] = True; # NodeCte is the first son of Node*         

            # Connecting gs with gn
            gn = Graph.concatenate(gs,gn)
            gn.__tensor[0,3,0] = True; 

            # Connnecting with graphList[k]
            n = gn.getNbNodes()
            gn = Graph.concatenate(gn,graphList[k])
            gn.__tensor[1,n,1] = True

        if CHECK:
            gn.checkConsistency('Graph.linearCrossover (1)')

        gn.mutationKeepBest()
        gn.mutationShortenGraph()

        if CHECK:
            gn.checkConsistency('Graph.linearCrossover (2)')

        return gn




