print "  "
print "***** DEBUT *****************************************************"
from Node import *
from Tree import *
from RefModel import *


Node.opListLoad("../FichierTexteInput/ListeOperateur.txt")




print "Liste des operateurs"
print "   "+str(Node.getAllOp())


M = RefModel("../ModeleRef/Modele_small.txt")
Node.setRefModel(M)


print "******0010*********"
t = Tree()
t.createRandomTree()
t.certify()
t.printByLevel()

print t.getTextString()
print t.getLatexString()

t.getResult()

t2 = Tree()
t2.duplicate(t)
print t == t2

print t2.getResult()


t2.shortenTree()

quit()
print t2.getTextString()
print t == t2

print "getNbNodes : " + str(t.getNbNodes())
#print "getNodes : " + str(t.getNodes())
print "******0020*********"
t.certify()
t.printByLevel()

print "*******0030********"



n1 = t.getNodes()[0]
n2 = n1.father[0].father[0]
print n1.id
print n2.id
print "*******0040********"
t.certify()
print n1.isAncestor(n2)

print "*******0050********"
print "Croisement avec father multiple"
t.rootNode.type = "bn"
t.rootNodevalue = "+"
t.rootNode.right = t.rootNode.left.left

t.certify()
t.printByLevel()

print "*******0060********"
print "PasteTree"

t1 = Tree()
t1.createRandomTree()
t2 = Tree()
t2.createRandomTree()

print t1.getTextString()
print
for i in xrange(10):
    n1 = t1.getNodes()[t1.getRandomNodeIndex()]
    n2 = t2.getNodes()[t2.getRandomNodeIndex()]
    t2.pasteNode(n2,n1)
    t2.certify()
    print t2.getTextString()
    t2.rootNode.getResult()

print "***** FIN ******"
print "  "

















