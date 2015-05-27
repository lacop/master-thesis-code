# TODO notes
# Optimize - generate clauses/variables on the fly, dont keep references to left/right operands
#            so that python runtime can GC them if not required
#          - propagate constants, ...


class BitVector():
    def __init__(self, size):
        self.size = size
        self.bits = [None]*size
        self.vars = [None]*size
        self.printed = False
        self.assigned = False
    def getBit(self, i):
        return self.bits[i]
    def __str__(self):
        return ' '.join([str(self.getBit(i)) for i in range(self.size)])
    def assignVars(self, instance):
        if self.assigned:
            return
        self.assigned = True
        for i in range(len(self.vars)):
            if self.vars[i] is None:
                self.vars[i] = instance.getNewVariable()
    def printClauses(self, f):
        if self.printed:
            return
        self.printed = True
        for i in range(len(self.bits)):
            if self.bits[i] is not None:
                f.write('{} 0\n'.format(self.vars[i] * (1 if self.bits[i] else -1)))
    def verify(self, instance):
        for i in range(len(self.bith)):
            if self.bits[i] is not None:
                assert self.bits[i] == instance.getVar(self.vars[i])
            # TODO
            #assert self.getBit(i) == instance.getVar(self.vars[i])
    def getValuation(self, instance):
        return [instance.getVar(self.vars[i]) for i in range(self.size)]

    def getParents(self):
        return []

    def __and__(self, other):
        return OperatorAnd(self, other)
    def __or__(self, other):
        return OperatorOr(self, other)
    def __xor__(self, other):
        return OperatorXor(self, other)
    # TODO autocast from int to constant
    def __add__(self, other):
        return OperatorAdd(self, other)
    def __invert__(self):
        return OperatorNot(self)


class ConstantVector(BitVector):
    def __init__(self, bits):
        BitVector.__init__(self, len(bits))
        self.bits = bits
    def printClauses(self, f):
        BitVector.printClauses(self, f)

# Todo universal operator with getbit/print lambdas
class BinaryOperator(BitVector):
    def __init__(self, left, right):
        assert left.size == right.size
        BitVector.__init__(self, left.size)
        self.left = left
        self.right = right

    def getParents(self):
        return [self.left, self.right]

    def assignVars(self, instance):
        if self.assigned:
            return

        self.left.assignVars(instance)
        self.right.assignVars(instance)
        BitVector.assignVars(self, instance)
        self.assigned = True
    def printClauses(self, f):
        if self.printed:
            return

        self.left.printClauses(f)
        self.right.printClauses(f)

        BitVector.printClauses(self, f)
        self.printOperatorClauses(f)
        self.printed = True
    def printOperatorClauses(self, f):
        pass

class NaryOperator(BitVector):
    def __init__(self, *operands):
        self.operands = operands
        BitVector.__init__(self, operands[0].size)

    def getParents(self):
        return list(self.operands)

    def assignVars(self, instance):
        if self.assigned:
            return
        for op in self.operands:
            op.assignVars(instance)
        BitVector.assignVars(self, instance)
        self.assigned = True
    def printClauses(self, f):
        if self.printed:
            return
        for op in self.operands:
            op.printClauses(f)
        BitVector.printClauses(self, f)
        self.printOperatorClauses(f)
        self.printed = True
    def printOperatorClauses(self, f):
        pass

class UnaryOperator(BitVector):
    def __init__(self, vector):
        BitVector.__init__(self, vector.size)
        self.vector = vector

    def getParents(self):
        return [self.vector]

    def assignVars(self, instance):
        if self.assigned:
            return

        self.vector.assignVars(instance)
        BitVector.assignVars(self, instance)
        self.assigned = True
    def printClauses(self, f):
        if self.printed:
            return

        self.vector.printClauses(f)

        BitVector.printClauses(self, f)
        self.printOperatorClauses(f)
        self.printed = True
    def printOperatorClauses(self, f):
        pass

class CyclicLeftShift(UnaryOperator):
    def __init__(self, vector, amount):
        UnaryOperator.__init__(self, vector)
        self.amount = amount
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> Y       as CNF:     X | ~Y
            #                           ~X | Y
            j = (self.size+i-self.amount) % self.size
            f.write('{} {} 0\n'.format(self.vars[i], -1*self.vector.vars[j]))
            f.write('{} {} 0\n'.format(-1*self.vars[i], self.vector.vars[j]))

class LeftShift(UnaryOperator):
    def __init__(self, vector, amount):
        UnaryOperator.__init__(self, vector)
        self.amount = amount
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> Y       as CNF:     X | ~Y
            #                           ~X | Y
            j = i-self.amount
            if j >= 0 and j < self.size:
                f.write('{} {} 0\n'.format(self.vars[i], -1*self.vector.vars[j]))
                f.write('{} {} 0\n'.format(-1*self.vars[i], self.vector.vars[j]))
            else:
                f.write('{}\n'.format(-1*self.vars[i]))

class OperatorNot(UnaryOperator):
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> ~Y       as CNF:    X | Y
            #                           ~X | ~Y
            f.write('{} {} 0\n'.format(self.vars[i], self.vector.vars[i]))
            f.write('{} {} 0\n'.format(-1*self.vars[i], -1*self.vector.vars[i]))

class OperatorOr(NaryOperator):
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> A1 | A2 | ... | AN as CNF: X | ~Ai for each i
            #                                  ~X | A1 | A2 | ... | AN
            for op in self.operands:
                f.write('{} {} 0\n'.format(self.vars[i], -1*op.vars[i]))
            f.write('{} '.format(-1*self.vars[i]))
            for op in self.operands:
                f.write('{} '.format(op.vars[i]))
            f.write('0\n')

class OperatorAnd(NaryOperator):
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> A1 & A2 & ... & AN as CNF: ~X | Ai for each i
            #                                  X | ~A1 | ~A2 | ... | ~AN
            for op in self.operands:
                f.write('{} {} 0\n'.format(-1*self.vars[i], op.vars[i]))
            f.write('{} '.format(self.vars[i]))
            for op in self.operands:
                f.write('{} '.format(-1*op.vars[i]))
            f.write('0\n')


class BinaryOperatorAnd(BinaryOperator):
    def getBit(self, i):
        return self.left.getBit(i) & self.right.getBit(i)
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> L & R   as CNF:     L | ~X
            #                           R | ~X
            #                           X | ~L | ~R
            f.write('{} {} 0\n'.format(self.left.vars[i], -1*self.vars[i]))
            f.write('{} {} 0\n'.format(self.right.vars[i], -1*self.vars[i]))
            f.write('{} {} {} 0\n'.format(self.vars[i], -1*self.left.vars[i], -1*self.right.vars[i]))

class BinaryOperatorOr(BinaryOperator):
    def getBit(self, i):
        return self.left.getBit(i) | self.right.getBit(i)
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> L | R   as CNF:     ~L | X
            #                           ~R | X
            #                           ~X | L | R
            f.write('{} {} 0\n'.format(-1*self.left.vars[i], self.vars[i]))
            f.write('{} {} 0\n'.format(-1*self.right.vars[i], self.vars[i]))
            f.write('{} {} {} 0\n'.format(-1*self.vars[i], self.left.vars[i], self.right.vars[i]))

class OperatorXor(BinaryOperator):
    def getBit(self, i):
        return self.left.getBit(i) ^ self.right.getBit(i)
    def printOperatorClauses(self, f):
        for i in range(len(self.vars)):
            # X <-> L ^ R   as CNF:     X | ~L | R
            #                           X | L | ~R
            #                           ~X | ~L | ~R
            #                           ~X | L | R
            f.write('{} {} {} 0\n'.format(self.vars[i], -1*self.left.vars[i], self.right.vars[i]))
            f.write('{} {} {} 0\n'.format(self.vars[i], self.left.vars[i], -1*self.right.vars[i]))
            f.write('{} {} {} 0\n'.format(-1*self.vars[i], -1*self.left.vars[i], -1*self.right.vars[i]))
            f.write('{} {} {} 0\n'.format(-1*self.vars[i], self.left.vars[i], self.right.vars[i]))

class OperatorAdd(BinaryOperator):
    def __init__(self, left, right):
        BinaryOperator.__init__(self, left, right)
        self.vars = [None] * 2*self.size
    def assignVars(self, instance):
        BinaryOperator.assignVars(self, instance)
        self.carry = [self.vars[i+self.size] for i in range(self.size)]
    def getBit(self, i):
        # TODO
        return False
    def printOperatorClauses(self, f):
        f.write('-{} 0\n'.format(self.carry[0]))
        #f.write('-{} 0\n'.format(self.carry[self.size-1]))

        for i in range(self.size):
        #for i in range(self.size-1, -1, -1):
            # X <-> (L ^ R ^ C) as CNF: X | ~L | ~R | ~C
            #                           X | L | R | ~C
            #                           X | L | ~R | C
            #                           X | ~L | R | C
            #                           ~X | ~L | ~R | C
            #                           ~X | ~L | R | ~C
            #                           ~X | L | ~R | ~C
            #                           ~X | L | R | C
            f.write('{} -{} -{} -{} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('{} {} {} -{} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('{} {} -{} {} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('{} -{} {} {} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('-{} -{} -{} {} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('-{} -{} {} -{} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('-{} {} -{} -{} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            f.write('-{} {} {} {} 0\n'.format(self.vars[i], self.left.vars[i], self.right.vars[i], self.carry[i]))
            # C' <-> ((L | R) & (L | C) & (R | C)) as CNF:  X | ~L | ~C
            #                                               X | ~R | ~C
            #                                               X | ~L | ~R
            #                                               ~X | L | C
            #                                               ~X | R | C
            #                                               ~X | L | R
            if i+1 < self.size:
            #if i > 0:
                j = i+1
                #j = i-1
                f.write('{} {} {} 0\n'.format(self.carry[j], -1*self.left.vars[i], -1*self.carry[i]))
                f.write('{} {} {} 0\n'.format(self.carry[j], -1*self.right.vars[i], -1*self.carry[i]))
                f.write('{} {} {} 0\n'.format(self.carry[j], -1*self.left.vars[i], -1*self.right.vars[i]))
                f.write('{} {} {} 0\n'.format(-1*self.carry[j], self.left.vars[i], self.carry[i]))
                f.write('{} {} {} 0\n'.format(-1*self.carry[j], self.right.vars[i], self.carry[i]))
                f.write('{} {} {} 0\n'.format(-1*self.carry[j], self.left.vars[i], self.right.vars[i]))


class Instance:
    def __init__(self):
        self.varCount = 0
    def getNewVariable(self):
        self.varCount += 1
        return self.varCount
    def emit(self, output):#), optimizers=None):
        #if optimizers:
        #    print('Running optimizers')
        #    # TODO run multiple times until fixpoint
        #    for o in optimizers:
        #        for i in range(len(output)):
        #            output[i] = o.optimize(output[i])
        print('Setting variables...')
        for o in output:
            o.assignVars(self)
        f = open('instance.cnf', 'w')
        print('Generating clauses...')
        for o in output:
            o.printClauses(f)
        f.close()
    def read(self, path):
        self.vars = [None]*(self.varCount + 1)
        with open(path, 'r') as f:
            f.readline()
            for x in f.readline().strip().split():
                v = int(x)
                if v == 0:
                    break
                self.vars[abs(v)] = True if v > 0 else False
    def getVar(self, v):
        return self.vars[v]
    def verify(self, output):
        output.verify(self)