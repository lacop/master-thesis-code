# Implementations of some optimizations
#
# Please refer to the thesis text for explanation.

from library.instance import *

class Optimizer:
    def optimize(self, root):
        return root

class BinaryOperatorMergeOptimizer(Optimizer):
    def __init__(self, operatorType, maxArity = None):
        self.operatorType = operatorType
        self.maxArity = maxArity
    def optimize(self, root):
        if root.opt is not None:
            return root.opt
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
            #print('Merging', len(newops))
            root.opt = type(root)(*newops)
        else:
            if type(root) is CyclicLeftShift or type(root) is LeftShift:
                root.opt = type(root)(operands[0], root.amount)
            else:
                root.opt = type(root)(*operands)
        return root.opt


DefaultOrOperatorMerger = BinaryOperatorMergeOptimizer(OperatorOr)
DefaultAndOperatorMerger = BinaryOperatorMergeOptimizer(OperatorAnd)
# Avoid very large XORs, since it needs 2^arity clauses
DefaultXorOperatorMerger = BinaryOperatorMergeOptimizer(OperatorXor, 4)

class EspressoExpression(NaryOperator):
    def __init__(self, incnt, clauses, vectors):
        self.incnt = incnt
        self.clauses = clauses
        self.vectors = vectors
        self.operands = vectors
        BitVector.__init__(self, vectors[0].size)
        #print(clauses, incnt, vectors)
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            for clause in self.clauses:
                # TODO only true clauses?
                for j in range(self.incnt):
                    #print(i, clause, j, self.vectors[j].vars[i])
                    if clause[j] == '0':
                        f.write('{} '.format(self.vectors[j].vars[i]))
                    elif clause[j] == '1':
                        f.write('{} '.format(-1*self.vectors[j].vars[i]))
                #print(i, clause, self.vars[i])
                if clause[-1] == '0':
                    f.write(' {} 0\n'.format(-1*self.vars[i]))
                else:
                    f.write(' {} 0\n'.format(self.vars[i]))


# input: n-ary lambda, using only binary logical operators
# output: n-ary function, which for n bit vectors returns EspressoExpression
def OptimizeExpression(expr):
    from itertools import product
    from subprocess import call
    # TODO: verify expression uses just supported operators? (shifts won't work for example)

    incnt = expr.__code__.co_argcount

    espresso_input = '.i {}\n'.format(incnt)
    espresso_input += '.o 1\n'
    for inputs in product([0, 1], repeat=incnt):
        out = expr(*inputs)
        espresso_input += '{} {}\n'.format(''.join(str(x) for x in inputs), out)
    espresso_input += '.e\n'

    with open('opt.in', 'w') as f:
        f.write(espresso_input)
    print('Minimizing with espresso...')
    call(['./espressorun.sh', 'opt.in', 'opt.out'])
    l = open('opt.out').readlines()
    clauses = [x.strip() for x in l[4:-1]]

    def build(*vectors):
        assert len(vectors) == incnt
        return EspressoExpression(incnt, clauses, vectors)

    return build