# Sample showing how to use the Espresso expression optimization

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
from library.instance import *
from library.optimizers import *

instance = Instance()

X = BitVector(1)
Y = BitVector(1)
Z = BitVector(1)

# Unoptimized
F = (X & Y) ^ (~X & Z)

# Optimized
chopt = OptimizeExpression(lambda x,y,z: (x&y) ^ (~x&z))
F = chopt(X, Y, Z)

instance.emit([F])
instance.solve(['minisat'])

print('X', X.getValuation(instance))
print('Y', Y.getValuation(instance))
print('Z', Z.getValuation(instance))
print('F', F.getValuation(instance))