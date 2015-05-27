from instance import *

class Optimizer:
    def optimize(self, root):
        return root

# TODO redesign the optimzer
# now creates duplicates/... since it's DAG not a tree

class BinaryOperatorMergeOptimizer(Optimizer):
    def __init__(self, operatorType):
        self.operatorType = operatorType
    def optimize(self, root):
        operands = root.getParents()
        if len(operands) == 0:
            return root
        for i in range(len(operands)):
                operands[i] = self.optimize(operands[i])
        if type(root) is self.operatorType:
            newops = []
            for op in operands:
                if type(op) is self.operatorType:
                    newops += op.getParents()
                else:
                    newops.append(op)
            return type(root)(*newops)
        else:
            return type(root)(*operands)


DefaultOrOperatorMerger = BinaryOperatorMergeOptimizer(OperatorOr)
DefaultAndOperatorMerger = BinaryOperatorMergeOptimizer(OperatorAnd)