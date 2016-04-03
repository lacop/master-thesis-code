from instance import *
from optimizers import *
instance = Instance()

X = BitVector(1)
Y = BitVector(1)
Z = BitVector(1)

F = (X & Y) ^ (~X & Z)
#F.bits[0] = False
#X.bits[0] = True
#Y.bits[0] = True
#Z.bits[0] = True

chopt = OptimizeExpression(lambda x,y,z: (x&y) ^ (~x&z))
F = chopt(X, Y, Z)

instance.emit([F])
#stats = instance.solve('./cmsrunq.sh')
stats = instance.solve(['./minisatrun.sh'])
#print(stats)

print('X', X.getValuation(instance))
print('Y', Y.getValuation(instance))
print('Z', Z.getValuation(instance))
print('F', F.getValuation(instance))