# Import of the externals functions:
import os
import math
import numpy
import random

class RefModel():
    
    def __init__( self, name , param1=None ):

        self.__name = None
        self.__nbPoints = None
        self.__refFunction = None
        self.__refFunctionMean = None
        self.__refFunctionStd = None
        self.__variables = None
        self.__nbVariables = 0

        if name is not None:
            print "Model : "+name
            self.__name = name
            if name == "Polynome":
                self.buildPolynomeModel(param1)
            elif name == "Sextic":
                self.buildSexticModel()
            elif name == "Quintic":
                self.buildQuinticModel()
            elif name == "X2":
                self.buildX2Model()
            else:
                self.loadModel(name)
            # In any case, compute the mean and std of variable and ref function
            self.computeMeanStd()
        else:
            print "No RefModel"

    def buildX2Model(self,degree):
        n = 21
        self.__nbPoints = n
        self.__nbVariables = 1
        x = numpy.linspace(-10,+10,n)
        self.__variables = [x]     
        self.__refFunction = pow(x,2)

    def buildSexticModel(self):
        n = 51
        self.__nbPoints = n
        self.__nbVariables = 1
        x = numpy.linspace(-3,+3,n)
        self.__variables = [x]     
        self.__refFunction = -pow(x,6)-pow(x,4)+pow(x,2)

    def buildQuinticModel(self):
        n = 51
        self.__nbPoints = n
        self.__nbVariables = 1
        x = numpy.linspace(-3,+3,n)
        self.__variables = [x]     
        self.__refFunction = -pow(x,5)-2*pow(x,3)+x

    def buildPolynomeModel(self,degree):
        n = 51
        self.__nbPoints = n
        self.__nbVariables = 1
        x = numpy.linspace(-3,+3,n)
        self.__variables = [x]     
        result = numpy.zeros(n)
        for i in range(degree+1):
            result += random.gauss(0,1) * pow(x,i)
        self.__refFunction = result


    def loadModel(self,name):
        print "Chargement du modele de reference"
        # Read the file of reference model:
        data = numpy.loadtxt(name)
        self.__nbPoints = data.shape[0]
        self.__nbVariables = data.shape[1]-1
        print "   Nombre de points du domaine d'apprentissage : " + str(self.__nbPoints)
        print "   Nombre de variables : " + str(self.__nbVariables)

        # Read the data type
        dataType = self.readDataType(name)

        # Build the matrix of input variables:
        self.__variables = []
        for i in range(self.__nbVariables):
            variableType = dataType[i]
            self.__variables.append(numpy.array(data[:,i],dtype=variableType))

        # Build the output variable:
        refModelType = dataType[-1]
        self.__refFunction = numpy.array(data[:, self.__nbVariables],dtype=refModelType)




    def computeMeanStd(self):
        self.__refFunctionMean = numpy.mean(self.__refFunction)
        self.__refFunctionStd = numpy.std(self.__refFunction)

        # Build the correlation of each variable
        self.__variablesCorrelation = []
        for i in range(self.__nbVariables):
            v = self.__variables[i]
            # Center data
            meanOfProduct = numpy.mean(v  * self.__refFunction) 
            productOfMean = numpy.mean(v) * self.__refFunctionMean
            # Calcul correlation (regardless of std and RefFunc)
            vCor = meanOfProduct - productOfMean
            # Take into account srd of result and RefFunc
            vCor /= numpy.std(v) * self.__refFunctionStd
            # keep abs value
            vCor = abs(vCor)
            # Save this.
            self.__variablesCorrelation.append( vCor )
        

    def readDataType(self, fileName):
        fid = open(fileName,'r')
        line = fid.readline()
        fid.close()
        if line[0] == "#":
            line = line.replace('#','').split()
        else:
            line = line.split()
            line = ['float']*len(line)
        print "   Input Data Type : "+str(line)
        return line

    def getName(self):
        return self.__name

    def setName(self,s):
        self.__name = s

    def getVariable(self, i):
        return self.__variables[i]

    def getNbPoints(self):
        return self.__nbPoints

    def setNbVariables(self,v):
        self.__nbVariables = v

    def getNbVariables(self):
        return self.__nbVariables

    def getRefFunction(self):
        return self.__refFunction

    def getRefFunctionMean(self):
        return self.__refFunctionMean

    def getRefFunctionStd(self):
        return self.__refFunctionStd

    def getVariableCorrelation(self, i):
        return self.__variablesCorrelation[i]


