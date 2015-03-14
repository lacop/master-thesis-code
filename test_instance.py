from instance import *

#A = BitVector(8)
#B = ConstantVector([1, 0, 0, 1, 0, 1, 1, 0])
#C = OperatorAnd(A, B)
#print(C)

#A = BitVector(4)
##A = ConstantVector([1, 1])
#B = ConstantVector([0, 1, 0, 0])
#C = OperatorAnd(A, B)
#D = ConstantVector([1, 0, 1, 0])
#E = OperatorOr(C, D)
#F = ConstantVector([1, 0, 0, 1])
#G = OperatorXor(E, F)
#H = CyclicLeftShift(G, 1)
##C = ConstantVector([1, 0, 1, 0])

#C.bits[0] = True
#C.bits[1] = True

A = ConstantVector([0, 1, 1, 0, 1, 1])
#B = ConstantVector([1, 1, 1, 0, 0, 1])
B = BitVector(6)
C = OperatorAdd(A, B)
C.bits = [True, False, True, True, True, False]
D = OperatorNot(C)

i = Instance()
#i.emit(H)
i.emit(D)

from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
i.read('instance.out')

#i.verify(H)
i.verify(D)

def toInt(X):
    val = 0
    for b in X.getValuation(i)[::-1]:
        val = val*2 + (1 if b else 0)
    return val

print('A', A.getValuation(i), toInt(A))
print('B', B.getValuation(i), toInt(B))
print('C', C.getValuation(i), toInt(C), toInt(A)+toInt(B), (toInt(A) + toInt(B)) % 2**(len(A.bits)))
print('D', D.getValuation(i))
#print('E', E.getValuation(i))
#print('F', F.getValuation(i))
#print('G', G.getValuation(i))
#print('H', H.getValuation(i))