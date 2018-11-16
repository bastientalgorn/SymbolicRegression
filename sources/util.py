# -*- mode: python; py-indent-offset: 4; tab-width: 4; coding: iso-8859-1 -*-

# Importation of the extern functions :
import os
import numpy
import random
import sys
import math
import datetime
import time

# machine precision
MACHINE_EPS = numpy.finfo(numpy.float32).eps

def isDiff(x,y):
    # Determine if there is a significant difference between two vectors
    diff = numpy.abs(x-y)
    norm = numpy.minimum(numpy.abs(x),numpy.abs(y))
    #norm = numpy.maximum(norm,MACHINE_EPS)
    return numpy.any(diff > MACHINE_EPS*(1+norm))

def isDiffScalar(x,y):
    # Determine if there is a significant difference between two scalars
    diff = numpy.abs(x-y)
    if diff < MACHINE_EPS:
        return False
    norm = numpy.minimum(numpy.abs(x),numpy.abs(y))
    #norm = numpy.maximum(norm,MACHINE_EPS)
    return diff > MACHINE_EPS*(1+norm)


def isDiff2(x,y):
    # To save time, the following heuristic if used:
    # - The first value of each vector are compared with a large tolerance
    # - If this first comparison shows differences, then the vectors are considered as different.
    # - Else, a comparison of the full vectors is performed.

    # Extract the FIRST value of each vector
    if not (len(numpy.atleast_1d(x))==1 or len(numpy.atleast_1d(y))==1):
        x1 = x[1]
        y1 = y[1]
 
        # Comparison of the FIRST value
        diff = numpy.abs(x1-y1)
        norm = numpy.minimum(numpy.abs(x1),numpy.abs(y1))
        norm = numpy.maximum(norm,MACHINE_EPS)
        if diff > MACHINE_EPS*(10+norm):
            return True

    # Determine if there is a significant difference between two vectors
    diff = numpy.abs(x-y)
    norm = numpy.minimum(numpy.abs(x),numpy.abs(y))
    norm = numpy.maximum(norm,MACHINE_EPS)
    return numpy.any(diff > MACHINE_EPS*(1+norm))


def isDiff3(x,y):
    # To save time, the following heuristic if used:
    # - The first value of each vector are compared with a large tolerance
    # - If this first comparison shows differences, then the vectors are considered as different.
    # - Else, a comparison of the full vectors is performed.

    xScalar = (len(numpy.atleast_1d(x))==1)
    yScalar = (len(numpy.atleast_1d(y))==1)

    # Extract the FIRST value of each vector
    if not (xScalar or yScalar):
        x1 = x[1]
        y1 = y[1]

        # Comparison of the FIRST value
        diff = numpy.abs(x1-y1)
        norm = numpy.minimum(numpy.abs(x1),numpy.abs(y1))
        norm = numpy.maximum(norm,MACHINE_EPS)
        if diff > MACHINE_EPS*(10+norm):
            return True

    # Determine if there is a significant difference between two vectors
    diff = numpy.abs(x-y)
    norm = numpy.minimum(numpy.abs(x),numpy.abs(y))
    norm = numpy.maximum(norm,MACHINE_EPS)
    return numpy.any(diff > MACHINE_EPS*(1+norm))





def removeParenthesis(s):
    # Suppression des parenthèses de début et de fin
    change = True
    while change:
        change = False
        tab = getParenthesisStructure(s)
        if len(tab) and tab[-1][0]==0 and tab[-1][1]==len(s)-1:
                s = s[1:-1]
                change = True

    # Suppresion of double parenthesis
    change = True
    while change:
        change = False
        tab = getParenthesisStructure(s);
        for i in range(len(tab)-1):
            [a,b] = tab[i]
            if a==tab[i+1][0]+1 and  b==tab[i+1][1]-1:
                s = s[:a-1]+s[a:b]+s[b+1:]
                change = True
                break
    return s

def getParenthesisStructure(s):
    pile = []
    p = []
    for i in range(len(s)):
        if s[i]=='(':
            pile.append(i)
        elif s[i]==')':
            k = pile.pop(-1) # Remove the last element
            p.append([k,i])
    return p

def printBooleanMatrix(B):
    NI = B.shape[0]
    NJ = B.shape[1]
    print NI
    print NJ
    print str(B)

# Get a random float...
def symmetricExp(expParameter=3):
    x = random.expovariate(expParameter)
    p = random.random()
    if p > 0.5:
        return x
    else:
        return -x

def getDate():
    d = datetime.datetime.now()
    return str(d.year)+"_"+str(d.month)+"_"+str(d.day)+"_"+str(d.hour)+"h"+str(d.minute)+"m"+str(d.second)+"s"

def setSeed(seed=None):
    if seed is None:
        # If no seed is specified, then a seed is build from the clock
        seed = float(str(time.time()))
    elif seed is "last":
        # If the seed is the word "last", then the last seed is used
        fid = open("seed.txt","r")
        seed = float(fid.read())
        fid.close()

    # The seed is printed on the screen
    #print "Random Seed : "+str(seed)
    # And written in a file
    fid = open("seed.txt","w")
    fid.write(str(seed))
    fid.close()
    random.seed(seed)
        


def indexChoice(eligible,criteria=None,criteriaDirection="high"):
    # This function allow to choose an index in a list of possible index
    # eligibility is a numpy boolean vector of N elements
    # criteria is a numpy real vector of N elements

    # A index i can be chosen if eligibility[i] == True

    # If no criteria is given, the choice will be made uniformly among the eligible indexes.
    # If criteria is given, the "Roulette biaisée" rule will be used.
    # If criteriaDirection is "high", the high criteria values will be privileged.
    # If -------------------- "low",  the low -----------------------------------.
    N = len(eligible) 

    # Vérification d'usage
    if (criteria is not None) and (len(criteria)!=N):
        print "Error dans indexChoice"
        print "len(eligible) = "+str(N)
        print "len(criteria) = "+str(len(criteria))
        return None

    if not numpy.any(eligible):
        return None

    # Liste des indices éligibles
    eligibleIndexes = []
    for i in range(N):
        if eligible[i]:
            eligibleIndexes.append(i)

    if criteria is None:
        if len(eligibleIndexes):
            # Uniform choice among the eligible indexes
            return random.choice(eligibleIndexes)
        else:
            return None
    else:
        # Prise en compte du critere
        #print "crit : "+str(criteria)
        # Si on veut un critère faible, alors on oppose la valeur du critère
        if criteriaDirection is "low":
            for i in eligibleIndexes:
                criteria[i] *= -1.0

        # Construction du tableau contenant les indices et les critères
        liste=[]
        for i in eligibleIndexes:
            liste.append([i,criteria[i]])

        # Classement en fonction du critère
        liste.sort(cmp=lambda x,y: cmp(x[1], y[1]))

        # Tirage d'un sous indice entre 0 et NE-1
        NE = len(eligibleIndexes)
        r = random.random()
        subIndex = int(math.ceil((numpy.sqrt(1+4*r*NE*(NE+1))-1)/2)-1)
        return eligibleIndexes[subIndex]


def cleanLines(lines):
    for i in range(len(lines)):
        line = lines[i]
        line = line.strip()
        line.replace("\n","").replace("\r","").replace("\t","").replace("  "," ")
        lines[i] = line
    return lines

def getField(lines,fieldName):
    field = []
    fieldName = fieldName.lower()
    fieldIsOpen = False
    lines = cleanLines(lines)

    for line in lines:
        if len(line) and line[0]=="#":
            if line.lower()=="# "+fieldName:
                fieldIsOpen = True
            else:
                if fieldIsOpen:
                    return field
        else:
            if fieldIsOpen and len(line):
                field.append(line)
    return field

def quit(quitFile=None):
    print "***********************************************************************"
    print "Symbolic regression has stopped."
    if quitFile is not None:
        print "in file: "
        print quitFile
    print "***********************************************************************"
    sys.exit()




    

