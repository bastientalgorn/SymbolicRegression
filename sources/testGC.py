import numpy

N = 10
NC = 5
i = 1
T = numpy.zeros([N,N,NC],dtype=bool)     

T[i,3,0] = True
T[i,8,1] = True
T[i,2,2] = True

print T[i,:,:]

print numpy.nonzero(T[i,:,:])
print numpy.nonzero(T[i,:,:].transpose())
print numpy.nonzero(T[i,:,:].transpose())[1]


authorizedWords = [ 
            ['ind','Write the \'.ind\' file (Description of the individual)'],
            ['m','Write the \'.m\' file (Matlab file)'],
            ['pdf','Write the \'.pdf\' file (Graphic visualization of the Graph)'],
            ['dot','Write the \'.dot\' file (Source code for the pdf file)'],
            ['convergence','Write convergence file'],
            ['pareto-history','xxx','Write Pareto history'],
            ['current','Write current best individual at each generation'],
            ['duration','Write the duration of each generation'],
            ['superind','Compute a super-individual at each generation'],
            ['operator','Display the list of operators'],
            ['improvement','Display all improvements'],
            ['end-pareto','xxx','Write the complete pareto front (End of optimization)'],
            ['end-node-call','Write the number H calculations (End of optimization)'],
            ['end-sigma','Write sigma-obj1 in a file (End of optimization)']
]

print authorizedWords
