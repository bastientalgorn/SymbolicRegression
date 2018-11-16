# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-

import numpy
import util
import random
import re

class OpManager():

    def __init__(self, opFile=None):
        self.__listOperators = []
        self.__listNbArg = []
        self.__maxNbArg = 0
        self.__nbOperators = 0
        self.__listString = []
        self.__listOriginalString = []

    def loadOpFile(self, opFile):
        print "Loading the set of operators in file: "+opFile

        # Get the lines
        fid = open(opFile)
        lines = fid.readlines()
        fid.close()

        lines = util.cleanLines(lines)

        # Get the "# operators" field
        if opFile[-4:]==".ind":
            print "Extraction of the \"# operators\" field."
            lines = util.getField(lines,'operators')

        # Process
        mat = []
        for line in lines:
            values = line.replace(' ','').split(';')
            if "" in values:
                values.remove("")
            mat.append(values)
         # Filling the list of the operators:
        for nOp in range(0,len(mat)):
            operatorName = mat[nOp].pop(0).strip()
            # Find if the operator is "on" or "off"
            bool_on  = mat[nOp].count("on")>0
            bool_off = mat[nOp].count("off")>0
            # Check that the operator is not "on" AND "off" at the same time
            if bool_on and bool_off:
                print "The operator \""+operatorName+"\" is defined as \"on\" AND \"off\" !"
                print "Please check in file: "+opFile
                util.quit(__file__)
            # Remove "on" and "off" from list
            if bool_on:
                mat[nOp].remove("on")
            if bool_off:
                mat[nOp].remove("off")
            # If the arg is not "off", then it's "on"
            bool_on = bool_on or (not bool_off)            

            # Search for another name for the operator
            if bool_on:
                # Look for quotes in the list
                quoteNumber = 0
                opString = ""
                for elem in mat[nOp]:
                    if "\"" in elem:
                        quoteNumber += 1
                        opString = elem
                        
                if quoteNumber > 1:
                    print "The operator \""+operatorName+"\" has several interpretation strings !"
                    print "There is several fields with \"quotes\""
                    print "Please check in file: "+opFile        
                    util.quit(__file__)
                elif quoteNumber == 1:
                    mat[nOp].remove(opString)
                    opString = opString.replace('\"','')
                    opOriginalString = opString
                    if opString.count("(")!=opString.count(")"):
                        print "The operator \""+operatorName+"\" has improper number of parenthesis !"
                        print "Please check in file: "+opFile   
                        util.quit(__file__)   
                else:
                    opOriginalString = ""
                    opString = operatorName     


                # Check that the remaining arguments are digits and convert them to integer
                for i in range(len(mat[nOp])):
                    if mat[nOp][i].strip().isdigit():
                        # N is the order with which the operator is define
                        mat[nOp][i] = int(mat[nOp][i])
                    else:
                        print "The operator \""+operatorName+"\" is defined with unrecognised option \""+elem+"\""
                        print "Please check in file: "+opFile        
                        util.quit(__file__)    
                    
                # save original string and Narg of operators
                self.__listOriginalString.append([operatorName , mat[nOp], opOriginalString])


                for N in mat[nOp]:
                    # BUILD completeString 
                    if opString.count("(")==0:
                        if self.useNoParenthesis(operatorName):
                            completeString = "("
                            for i in range(N-1):
                                completeString += "$x"+str(i)+"$"+opString
                            completeString += "$x"+str(N-1)+"$)" 
                        else:
                            completeString = opString+"($x*$)"
                    else:
                        # nb : if opString contains parenthesis, then
                        # it is supposed to contain $x*$ or $xi$, so it don't need
                        # any change.
                        completeString = opString
  
                    # Replace $x*$
                    if completeString.count("$x*$"):
                        repx = ""
                        for i in range(N-1):
                            repx += "$x"+str(i)+"$,"
                        repx += "$x"+str(N-1)+"$" 
                        completeString = completeString.replace("$x*$",repx)

                    # Check that arguments "$x1$", "$x2", ... are in the range
                    listArg = re.findall("\$x[0-9]*\$",completeString)
                    listIndexes = []
                    for arg in listArg:
                        # get the index of the argument 
                        # $x13$ will give index 13.
                        index = int(arg.replace('$','').replace('x',''))
                        listIndexes.append(index)
                        # check that this index is smaller to ther order
                        if index>=N:
                            print "The operator \""+operatorName+"\" is defined with"
                            print "    String : "+opString
                            print "    order N="+str(N)
                            print "String must be defined with argument $xi$,"
                            print "    where i is in [0..."+str(N-1)+"]"
                            print "You can not use "+arg
                            print "Nb : you can also use $x*$ to which will be replaced by :"
                            print "     $x0$,$x1$,$x2$,...,$x"+str(N-1)+"$"
                            print "Please check in file: "+opFile        
                            util.quit(__file__)

                    # check that this index is smaller to ther order
                    if len(set(listIndexes))<N:
                        print "The operator \""+operatorName+"\" is defined with"
                        print "    String : "+opString
                        print "    Order N="+str(N)
                        print "Missing argument indexes : "+str([i for i in range(N) if i not in listIndexes])
                        print "Please check in file: "+opFile        
                        util.quit(__file__)

                    # save operator along with narg
                    self.__listOperators.append(operatorName)
                    self.__listNbArg.append(N)
                    self.__listString.append(completeString)    
                    self.__maxNbArg = max(self.__maxNbArg,N)
        self.printOperatorList()
              

    def printOperatorList(self):
        print "***********************************************************************"
        print "   Number of operators = "+str(self.getNbOperators())
        print "   maxNbArg = "+str(self.__maxNbArg)
        print "   meanNbArg = "+str(self.getMeanNbArg())
        # Display operators by nbArg :
        print "   Operators, by order :"
        for i in range(1,self.__maxNbArg+1):
            print "\t"+str(i)+" arg operators : "+str(self.getListOp(i))
        print "   All operators :"
        for i in range(len(self.__listOperators)):
            print "\t"+str(self.__listNbArg[i])+" "+self.__listOperators[i]+"\t"+self.__listString[i]
            #print self.getString(self.__listOperators[i],self.__listNbArg[i])
        print "***********************************************************************"

    def printListOriginalString(self):
        print "----------"
        for op in self.__listOriginalString:
            s = op[0]
            while len(s)<10:
                s+=' '
            s+=str(op[1])+" "+op[2]
            print s
            for na in op[1]:
                print "                 ----> "+self.getString(op[0],na)
        print "----------"

    def getOriginalString(self,opName):
        originalString = [z for (x,y,z) in self.__listOriginalString if x==opName]
        if len(originalString):
            return originalString[0]
        else:
            util.quit('OpManager.py')



    def getNbOperators(self,nbArg=None):
        # Return number of operators,
        # Or number of operators with a given nbArg
        if nbArg is None:
            return len(self.__listOperators)
        else:
            count = 0
            for i in range(self.getNbOperators()):
                if self.__listNbArg[i] == nbArg:
                    count += 1
            return count

    def getListOp(self,nbArg):
        # Return all operators for a given nbArg
        liste = []
        for i in range(self.getNbOperators()):
            if self.__listNbArg[i] == nbArg:
                liste.append( self.__listOperators[i] )
        return liste



    def getMaxNbArg(self):
        return self.__maxNbArg



    def getMeanNbArg(self):
        # Return average nbArg
        # This is useful to generate graphs with an expected number of nodes
        n = self.getNbOperators()  
        mean = 0.0  
        for i in range(n):
            mean += float(self.__listNbArg[i])
        mean = mean / float(n)
        return mean


    def getRandomOp(self):
        # Pick an operator randomly
        n = self.getNbOperators()  
        i = random.choice(range(n))
        # Return operator and nbArg
        return [self.__listOperators[i],self.__listNbArg[i]]


    def useNoParenthesis(self,op):
        return (op in ["+","*","/","-","^"])

    def isSymmetric(self,op):
        return (op in ["+","*","min","max","and","or","xor"])



    def exists(self,op,nbArg=None):
        if nbArg is None:
            return (op in self.__listOperators)
        else:
            return (op in self.getListOp(nbArg))

    def getString(self, opValue, opNbArg):
        for i in range(len(self.__listOperators)):
            if (self.__listOperators[i] == opValue) and (self.__listNbArg[i] == opNbArg):
                return self.__listString[i]


    def computeOperator(self, opValue, opNbArg, args):
        # Args must be provided as a list of numeric value
        result = None
        if self.isSymmetric(opValue):
            # symetric operators 
            result = args[0]
            r = range(1,opNbArg)
            if opValue == "+":
                for i in r:
                    result = result + args[i]
            elif opValue == "*":
                for i in r:
                    result = result * args[i]
            elif opValue == "max":
                for i in r:
                    result = numpy.maximum(result,args[i])
            elif opValue == "min":
                for i in r:
                    result = numpy.minimum(result,args[i])   
            elif opValue == "and":
                for i in r:
                    result = numpy.logical_and(result,args[i])    
            elif opValue == "or":
                for i in r:
                    result = numpy.logical_or(result,args[i])    
            elif opValue == "xor":
                for i in r:
                    result = numpy.logical_xor(result,args[i])    
        else:
            if opNbArg == 1:
                # Unary operators
                arg = args[0]
                if opValue == "sqrt":
                    result = numpy.sqrt(numpy.maximum(arg,0))
                elif opValue == "exp":
                    result = numpy.exp(arg)
                elif opValue == "log":
                    result = numpy.log(arg)
                elif opValue == "logabs":
                    result = numpy.log(abs(arg))
                elif opValue == "abs":
                    result = abs(arg)
                elif opValue == "sin":
                    result = numpy.sin(arg)
                elif opValue == "sinh":
                    result = numpy.sinh(arg)
                elif opValue == "cos":
                    result = numpy.cos(arg)
                elif opValue == "cosh":
                    result = numpy.cosh(arg)
                elif opValue == "tan":
                    result = numpy.tan(arg)
                elif opValue == "tanh":
                    result = numpy.tanh(arg)
                elif opValue == "sign":
                    result = numpy.sign(arg)
                elif opValue == "not":
                    result = numpy.logical_not(arg)

            elif opNbArg == 2:
                # Binary operators (non symmetric)
                arg0 = args[0]
                arg1 = args[1]
                if opValue == "-":
                    result = arg0 - arg1
                elif opValue == "/":
                    result = arg0 / arg1
                elif opValue == "^":
                    result = pow(arg0,arg1)                
                elif opValue == "powgen":
                    result = pow(numpy.abs(arg0),arg1) * numpy.cos(arg1*numpy.pi*(arg0<0))

            elif opNbArg == 3:
                # Trinary operators (non symmetric)
                arg0 = args[0]
                arg1 = args[1]
                arg2 = args[2]
                if opValue == "if":  
                    result = (arg0<0)*arg1 + (arg0>=0)*arg2

        return result





