# Import of the externals functions:
import os
import math
import numpy

class RefModel():
    
    def __init__( self, fileName ):

        print "Chargement du modele de reference"
        # Reading the file of reference model:
        data = numpy.loadtxt(fileName)

        self.__nbPoints = data.shape[0]
        self.__nbVariables = data.shape[1]-1
        print "   Nombre de points du domaine d'apprentissage : " + str(self.__nbPoints)
        print "   Nombre de variables : " + str(self.__nbVariables)

        # Build the matrix of input variables:
        self.__variables = []
        for i in range(self.__nbVariables):
            self.__variables.append(numpy.array(data[:,i]))

        # Build the output variable:
        self.__refFunction = data[:, self.__nbVariables]
        self.__refFunctionNormalised = (self.__refFunction-numpy.mean(self.__refFunction))/numpy.std(self.__refFunction)

        # Build the correlation of each variable
        self.__variablesCorrelation = []
        for i in range(self.__nbVariables):
            v = self.__variables[i]
            vNorm = ( v - numpy.mean(v) ) / numpy.std(v)
            vCor = abs(numpy.mean(vNorm * self.__refFunctionNormalised))
            self.__variablesCorrelation.append( vCor )
        

    def getVariable(self, i):
        return self.__variables[i]

    def getNbPoints(self):
        return self.__nbPoints

    def getNbVariables(self):
        return self.__nbVariables

    def getRefFunction(self):
        return self.__refFunction

    def getRefFunctionNormalised(self):
        return self.__refFunctionNormalised

    def getVariableCorrelation(self, i):
        return self.__variablesCorrelation[i]
