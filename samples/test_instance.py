# Few very simple samples of library usage

from instance import *
from optimizers import *
import itertools

def solve(vars):
    global i
    i.emit(vars)
    i.solve(['minisat'])

# Use library functions
i = Instance()
A = ConstantVector([0, 0, 1, 1, 0, 1, 0, 1])
B = ConstantVector([1, 0, 0, 1, 0, 1, 1, 0])
C = OperatorAnd(A, B)
solve([C])
print(C.getValuation(i))

# Same example, but seamlessly by using operator overloading
i = Instance()
A = ConstantVector([0, 0, 1, 1, 0, 1, 0, 1])
B = ConstantVector([1, 0, 0, 1, 0, 1, 1, 0])
C = A & B
solve([C])
print(C.getValuation(i))

# Restricting some bits
i = Instance()
A = BitVector(8)
B = BitVector(8)
X = A & B
Y = A + B
Z = A ^ B

X.bits = [False, True, True, False, False, True, True, False]
Y.bits = [True, None, None, False, None, True, None, None]
Z.bits = [True, None, False, None, None, False, None, None]

solve([A, B, X, Y, Z])
print(A.getValuation(i))
print(B.getValuation(i))
print(X.getValuation(i))
print(Y.getValuation(i))
print(Z.getValuation(i))