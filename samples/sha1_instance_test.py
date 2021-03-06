import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
from library.instance import *
from library.optimizers import *
from sha1_test import K, fs, sha1, digest_to_hex

# Little-endian
def intToVector(x, size=32):
    bits = [False]*size
    i = 0
    while x > 0:
        bits[i] = (x % 2 == 1)
        i += 1
        x //= 2
    return ConstantVector(bits)
# Little-endian bit list to int
def toInt(bits):
    val = 0
    for b in bits[::-1]:
        val = val*2 + (1 if b else 0)
    return val
# Big-endian bit list to int
def toIntBE(bits):
    return toInt(bits[::-1])

r1 = lambda b, c, d: (b & c) ^ (~b & d)
r24 = lambda b, c, d: b^c^d
r3 = lambda b, c, d: (b & c) ^ (b & d) ^ (c & d)

#r1 = OptimizeExpression(r1)
#r3 = OptimizeExpression(r3)

fs = [lambda a, b, c, d, e: r1(b, c, d),
      lambda a, b, c, d, e: r24(b, c, d),
      lambda a, b, c, d, e: r3(b, c, d),
      lambda a, b, c, d, e: r24(b, c, d)]

def main(mlength = None, rounds = None, out_file = None, out_bits = None):
    instance = Instance()
    Kvec = [intToVector(x) for x in K]

    #################### CONFIGURATION ####################
    # Original message length in bits
    if mlength is None:
        mlength = 8*4
    # Number of rounds, full SHA1 is 80
    if rounds is None:
        rounds = 80

    ###################### ENCODING #######################

    # For now just single block/chunk of 64bytes,
    # 14 blocks for data + padding, 2 blocks for length
    # Total of 16 blocks
    Mvec = [BitVector(32) for _ in range(14)]

    # Padding - "1", then "0" until 448 bits
    for i in range(mlength, 448):
        Mvec[i // 32].bits[31 - (i % 32)] = True if i == (mlength) else False

    # Original length, big-endian
    Mvec.append(intToVector(mlength // (2**32)))
    Mvec.append(intToVector(mlength % (2**32)))

    # Extend message to 80 32-bit words
    for i in range(16, 80):
        #Mvec.append(BitVector(32))
        Mvec.append(CyclicLeftShift(Mvec[i-3] ^ Mvec[i-8] ^ Mvec[i-14] ^ Mvec[i-16], 1))

    h0, h1, h2, h3, h4 = [intToVector(x) for x in [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]]

    roundvars = []

    A, B, C, D, E = h0, h1, h2, h3, h4
    for i in range(rounds):
        F = fs[i//20](A, B, C, D, E)
        k = Kvec[i//20]

        T = CyclicLeftShift(A, 5) + F + E + k + Mvec[i]
        A, B, C, D, E = T, A, CyclicLeftShift(B, 30), C, D
        roundvars.append((A, B, C, D, E))
    h0, h1, h2, h3, h4 = h0+A, h1+B, h2+C, h3+D, h4+E

    # TODO prettier
    # Generate CNF instance, solve, read
    print('Emit start')
    vars = [h0, h1, h2, h3, h4] + Mvec
    #for i in range(len(vars)):
    #    vars[i] = BinaryOperatorMergeOptimizer(OperatorXor, 6).optimize(vars[i])
    h0, h1, h2, h3, h4 = vars[:5]

    instance.assignVars(vars)# + [QQ])

    #################### CONFIGURATION ####################
    # Fix message/output bits here

    #Mvec[0].bits = [True]*32
    #h0.bits = [None]*24 + [True]*8
    if out_bits is not None:
        h0.bits = out_bits 

    #######################################################
    
    # Branching order
    #instance.branch(roundvars[0][0].vars)
    #for rv in roundvars[::-1]:
    #for rv in roundvars[::-1][::20]:\
    #for rv in [roundvars[-1], roundvars[-2], roundvars[-3]]:
    #for rv in roundvars[::8]:
    #for rv in [roundvars[0], roundvars[3]]:
    #     for v in [rv[4]]:
    #         instance.branch(v.vars)

    instance.emit(vars)# + [QQ])
    #stats = instance.solve('./cmsrunq.sh')
    stats = instance.solve(['./minisatrun.sh'])
    #from subprocess import call
    #call(['minisat', 'instance.cnf', 'instance.out'])
    #call(['./cmsrun.sh', 'instance.cnf', 'instance.out'])
    #instance.read('instance.out')

    # Get message bits
    Mbits = []
    for i in range(mlength):
        Mbits.append(Mvec[i // 32].getValuation(instance)[31 - (i % 32)])
    print('Message length', mlength, 'bits')#, Mbits)

    # Get digest bits
    Dbits = []
    for q in [h0, h1, h2, h3, h4][::-1]:
        Dbits += q.getValuation(instance)
    print('Digest', toInt(Dbits)) #, Dbits)

    # Assume 8bit multiple length, generate message
    # Then test with reference implementation for match
    message = b""
    for i in range(0, mlength//8):
        bits = Mvec[i//4].getValuation(instance)[(3-(i%4))*8 : (3-(i%4))*8 + 8]
        message += toInt(bits).to_bytes(1, byteorder='big')
    print ('Message bytes:', message, 'rounds: ', rounds)

    reference = sha1(message, rounds=rounds)
    print('sha1  ', reference, '  ', digest_to_hex(reference))
    assert reference == toInt(Dbits)
    print('MATCH!')

    if out_file is not None:
        with open(out_file, 'a') as f:
            # Write header
            if f.tell() == 0:
                f.write('rounds,time\n')
            f.write('{},{}\n'.format(rounds, stats['time']))

if __name__ == '__main__':
    main(rounds=80, out_bits = [None]*24 + [False]*8)
    #for _ in range(20):
    #    main(rounds=80, out_file='sha1-merge-on.csv')
    import itertools
    #for comb in itertools.product([True, False], repeat=8):
    #    main(rounds=80, out_file='sha1-merge-on.csv', out_bits = [None]*24 + list(comb))

