from instance import *

class Optimizer:
    def optimize(self, root):
        return root

# TODO redesign the optimzer
# now creates duplicates/... since it's DAG not a tree

class BinaryOperatorMergeOptimizer(Optimizer):
    def __init__(self, operatorType, maxArity = None):
        self.operatorType = operatorType
        self.maxArity = maxArity
    def optimize(self, root):
        operands = root.getParents()
        if len(operands) == 0:
            return root
        for i in range(len(operands)):
                operands[i] = self.optimize(operands[i])
        if type(root) is self.operatorType:
            # New arguments/operands for this operator
            newops = []
            for i in range(len(operands)):
                merge = True
                # Only merge same type
                if type(operands[i]) is not self.operatorType:
                    merge = False
                # Don't create higher arity than specified
                if self.maxArity:
                    if len(operands[i].getParents()) + len(newops) + (len(operands) - i - 1) > self.maxArity:
                        merge = False
                if merge:
                    newops += operands[i].getParents()
                else:
                    newops.append(operands[i])
            assert self.maxArity is None or len(newops) <= self.maxArity
            return type(root)(*newops)
        else:
            return type(root)(*operands)


DefaultOrOperatorMerger = BinaryOperatorMergeOptimizer(OperatorOr)
DefaultAndOperatorMerger = BinaryOperatorMergeOptimizer(OperatorAnd)

# TODO ?
DefaultXorOperatorMerger = BinaryOperatorMergeOptimizer(OperatorXor, 2)