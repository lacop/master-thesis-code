from instance import *
from optimizers import *

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

#A = ConstantVector([0, 1, 1, 0, 1, 1])
#B = ConstantVector([1, 1, 1, 0, 0, 1])
#B = BitVector(6)
#C = OperatorAdd(A, B)
#C = A + B
#C.bits = [True, False, True, True, True, False]
#D = ~C

i = Instance()
#i.emit(H)
#i.emit([D])

#A = ConstantVector([1, 0, 0, 0])
#B = ConstantVector([0, 1, 0, 0])
#C = ConstantVector([0, 1, 1, 0])
#D = ConstantVector([1, 0, 0, 1])

#Z = A ^ B ^ C ^ D
#X = DefaultOrOperatorMerger.optimize(X)
#Z = DefaultXorOperatorMerger.optimize(Z)
#i.emit([Z])#, [DefaultOrOperatorMerger])

import sys
sys.setrecursionlimit(10000)

#As = []
#size = 10
import itertools
#for v in itertools.product([0, 1], repeat=size):
#    As.append(ConstantVector(v))

#w = 4
#As = [BitVector(w) for _ in range(2**w)]
#X = As[0]
#Y = As[0]
#Z = As[0]
#for j in range(1, len(As)):
#    X = X | As[j]
#    Y = Y | As[j]
    #Y = Y & As[j]
    #Z = Z ^ As[j]

#Z = (X | Y) | (Y | X)

#X = DefaultOrOperatorMerger.optimize(X)
#Y = DefaultAndOperatorMerger.optimize(Y)
#Z = DefaultOrOperatorMerger.optimize(Z)
#i.emit([X])
#i.emit([Z])
#i.emit([X, Y, Z])

Q = BitVector(4)
for v in itertools.product([0, 1], repeat=4):
    Q = Q & ConstantVector(v)

As = [ConstantVector([False]*4)]
for j in range(20):
    As.append(As[-1] & Q)
Z = As[0]
for j in range(1, len(As)):
    Z = Z & As[j]

#Z = BinaryOperatorMergeOptimizer(OperatorXor, 10).optimize(Z)
Z = BinaryOperatorMergeOptimizer(OperatorAnd, 10).optimize(Z)

i.emit([Z])


#r3 = lambda b, c, d: (b & c) ^ (b & d) ^ (c & d)
#B, C, D = BitVector(4), BitVector(4), BitVector(4)
#F = r3(B, C, D)
#Z = r3(B, C, D)
#Z = B ^ C ^ D
#E = BitVector(4)

#Z = F + E
#Z = BinaryOperatorMergeOptimizer(OperatorXor, 6).optimize(Z)
#i.emit([Z])


#B = BitVector(1)
#C = BitVector(1)
#D = BitVector(1)
#
#F = (B & C) | (~B & D)

#i.emit([B, C, D, F])


#X = A ^ B ^ C ^ D

#X = A | B | C | D

#X = A+B+C+D+E
#i.emit([X])

#X = [A]
#for _ in range(7):
#    A = A + B
#i.emit([A])
#    X.append(X[-1] + B)
#C = X[-1]
#C = A + B
#C.bits = [True, False]
#D = C + B
#i.emit([C])
#i.emit([D])
#i.emit([C, D])

from subprocess import call
#call(['minisat', 'instance.cnf', 'instance.out'])
#i.read('instance.out')
#stats = i.solve(['./cmsrun.sh'])
stats = i.solve(['./minisatrun.sh'])

print(stats)
#i.verify(H)
#i.verify(D)

def toInt(X):
    val = 0
    for b in X.getValuation(i)[::-1]:
        val = val*2 + (1 if b else 0)
    return val

#print('A', A.getValuation(i))
#print('B', B.getValuation(i))
#print('C', C.getValuation(i))
#print('D', D.getValuation(i))
#print('F', F.getValuation(i))
#print()
#print('X', X.getValuation(i))
#print('Y', Y.getValuation(i))
print('Z', Z.getValuation(i))

#print('A', A.getValuation(i), toInt(A))
#print('B', B.getValuation(i), toInt(B))
#print('C', C.getValuation(i), toInt(C))
#print('D', D.getValuation(i), toInt(D))
#print('E', E.getValuation(i), toInt(E))
#print()
#print('X', X.getValuation(i), toInt(X))
#print(toInt(A) + toInt(B) + toInt(C) + toInt(D) + toInt(E))
#print((toInt(A) + toInt(B) + toInt(C) + toInt(D) + toInt(E)) % 2**len(A.bits))
#print('C', C.getValuation(i), toInt(C), toInt(A)+toInt(B), (toInt(A) + toInt(B)) % 2**(len(A.bits)))
#print('D', D.getValuation(i), toInt(D))
#print('E', E.getValuation(i))
#print('F', F.getValuation(i))
#print('G', G.getValuation(i))
#print('H', H.getValuation(i))