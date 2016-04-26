import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
from library.instance import *
from library.optimizers import OptimizeExpression

from sha3_reference import Keccak
import math

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
def toHexInt(bits):
    return hex(toInt(bits))

# Return/set n-th bit of a list of words
def nthbit(L, n, value=None):
    i = n // len(L[0].bits)
    j = n % len(L[0].bits)
    if value is not None:
        L[i].bits[j] = value
        #print(value, i, j)
    else:
        return L[i].bits[j]

def bitsToHex(bits):
    hex = ''
    for i in range(0, len(bits), 8):
        hex += ('00' + toHexInt(bits[i:i+8])[2:])[-2:]
    return hex

########################################################################################################################
# CONFIGURATION

# Hash function configuration
#r, c, sfx, n = , , 0x06,  # SHA3-224
#r, c, sfx, n = 1088, 512, 0x06, 256 # SHA3-256
#r, c, sfx, n = , , 0x06,  # SHA3-384
r, c, sfx, n = 576, 1024, 0x06, 512 # SHA3-512
# TODO fix values ^ and make padding work with all

msglen = 32 # In bits
roundlimit = 4 # Max is 24

# Don't change
msgbits = [None]*msglen
outbits = [None]*n

# Message/digest bit config
#msgbits = [False, False, False, True, True, True, False, False] #0x38
#print(msgbits)
#msgbits = []
#for i in range(msglen//8): # Printable ASCII
#    msgbits[i*8+7] = False
#    msgbits[i*8+6] = True

#outbits[:64] = [True]*64
outbits[:8] = ['ref']*8

#solver = ['timeout', '5', 'minisat']
solver = ['timeout', '5', './cmsrun.sh']
#solver = './cmsrun.sh'
#solver = 'minisat'

# def branchorder(i, rv):
#     for rnd in []:
#     # X, Y -> S[x][y]
#     #    for x in range(5):
#     #        for y in range(5):
#     #            i.branch(rv[rnd][0][x][y].vars) # S
#
#     # Y, X -> S[x][y]
#     #    for y in range(5):
#     #        for x in range(5):
#     #            i.branch(rv[rnd][0][x][y].vars) # S
#
#     # X, Y -> B[x][y]
#         for x in range(5):
#             for y in range(5):
#                 i.branch(rv[rnd][1][x][y].vars) # B
#
#     # X -> D[x]
#     #    for x in range(5):
#     #        i.branch(rv[rnd][2][x].vars) # C
#
#     # X -> D[x]
#     #    for x in range(5):
#     #        i.branch(rv[rnd][3][x].vars) # D

def main():
    def bo(i, rv):
        pass
    r = []
    for i in range(1):
        r.append(run_experiment(i, bo))

    print()
    print('----- REPORT -----')
    print(r)
    print('Time / Conflicts')
    #print('\t'.join(x['stats']['time'] for x in r))
    #print('\t'.join(str(x['stats']['conflicts']) for x in r))

########################################################################################################################

def run_experiment(extra_seed = 0, branch_order=None, use_espresso=False, xor_merge=True):
    global r, c, sfx, n, msglen, roundlimit, msgbits, outbits, solver, Keccak
    assert r%8 == 0
    assert n%8 == 0
    assert len(msgbits) == msglen

    instance = Instance()

    # Derived configuration
    b = r+c # TODO assert valid
    w = b // 25
    nr = 12 + 2*int(math.log(w, 2))

    if roundlimit == -1:
        roundlimit = nr
    assert roundlimit <= nr

    # Initial empty state
    S = [[intToVector(0, w) for _ in range(5)] for _ in range(5)]

    # Input message
    P = [BitVector(w) for _ in range(max(1, math.ceil(msglen / w)))]
    spos = 0
    while spos < msglen:
        nthbit(P, spos, msgbits[spos])
        spos += 1

    # Suffix
    sfxi = sfx
    while sfxi != 1:
        # TODO support when suffix needs to go to new vector
        nthbit(P, spos, sfxi % 2)
        sfxi //= 2
        spos += 1

    # Padding
    # TODO properly handle all cases
    nthbit(P, spos, True)
    spos += 1
    while spos < w: # TODO fix
        nthbit(P, spos, False)
        spos += 1
    for _ in range(7):
        P.append(intToVector(0, 64))
    P.append(intToVector(9223372036854775808, 64))

    roundvars = []

    Cfnc = lambda x,y,z,v,w: x ^ y ^ z ^ v ^ w
    if xor_merge:
        Cfnc = OptimizeExpression(Cfnc)
    Sfnc = lambda x,y,z: x ^ (~y & z)
    if use_espresso:
        Sfnc = OptimizeExpression(Sfnc)

    def rounds():
        #global S, roundvars
        for i in range(roundlimit):
            rc = intToVector(Keccak.RC[i], 64) # TODO truncate to w bits
            B = [[intToVector(0, w) for _ in range(5)] for _ in range(5)]
            C = [intToVector(0, w) for _ in range(5)]
            D = [intToVector(0, w) for _ in range(5)]

            for x in range(5):
                #C[x] = S[x][0] ^ S[x][1] ^ S[x][2] ^ S[x][3] ^ S[x][4]
                C[x] = Cfnc(S[x][0], S[x][1], S[x][2], S[x][3], S[x][4])
            for x in range(5):
                D[x] = C[(x-1)%5] ^ CyclicLeftShift(C[(x+1)%5], 1)
            for x in range(5):
                for y in range(5):
                    S[x][y] = S[x][y] ^ D[x]

            for x in range(5):
                for y in range(5):
                    B[y][(2*x+3*y)%5] = CyclicLeftShift(S[x][y], Keccak.r[x][y])

            for x in range(5):
                for y in range(5):
                    S[x][y] = Sfnc(B[x][y], B[(x+1)%5][y], B[(x+2)%5][y])

            S[0][0] = S[0][0] ^ rc

            roundvars.append(([row[:] for row in S], B, C, D))

    # Absorb
    for i in range(len(P)*64//r):
        Pi = P[i*r//w:(i+1)*r//w]
        for y in range(5):
            for x in range(5):
                idx = 5*y + x
                if idx < len(Pi):
                    S[x][y] = S[x][y] ^ Pi[idx]
        rounds()

    # Squeeze
    # TODO variable length output, bitrate output only, do rounds inbetween
    out = []
    for y in range(5):
        for x in range(5):
            out.append(S[x][y])

    # Generate reference digest for output bit fixing
    import random
    from zlib import adler32
    rnd = random.Random()
    seedstr = str(msglen) + str(roundlimit) +  ''.join(str(x) for x in msgbits) +  ''.join(str(x) for x in outbits) + str(extra_seed)
    seed = adler32(seedstr.encode()) & 0xffffffff
    rnd.seed(seed)

    refout_msg = ''.join(('00'+hex(rnd.randint(0, 255))[2:])[-2:] for _ in range(msglen//8))
    refout_k = Keccak(roundlimit=roundlimit)
    refout_digest = refout_k.Keccak((msglen, refout_msg), r, c, sfx, n)

    # Fix output bits
    for i in range(n):
        if outbits[i] == 'ref':
            nthbit(out, i, int(refout_digest[(i//8)*2:(i//8)*2 + 2], 16) & (1 << (i % 8)))
        else:
            nthbit(out, i, outbits[i])

    # SOLVE

    instance.assignVars(out + P)
    # Branching order
    if branch_order is not None:
        branch_order(instance, roundvars)
    instance.emit(out + P)

    print('Starting solver')
    stats = instance.solve(solver)
    if stats is None or stats['satisfiable'] is False:
        return None

    # Output/verify
    message = []
    for i in range(msglen):
        message.append(P[i//w].getValuation(instance)[i%w])
    print('message:', message)
    msg = (msglen, bitsToHex(message))

    mb = b''
    for i in range(msglen//8):
        mb += toInt(P[i*8//w].getValuation(instance)[(i*8)%w:(i*8)%w + 8]).to_bytes(1, byteorder='big')
    print('message:' , msg, mb)

    digest = ''
    for q in out:
        dx = ('0'*(w//4) + toHexInt(q.getValuation(instance))[2:])[-w//4:]
        for i in range(len(dx)//2):
            digest += dx[-2*(i+1):][:2]
    digest = digest[:2*n//8]
    print('digest:   ', digest.upper())

    from sha3_reference import Keccak
    k = Keccak(roundlimit=roundlimit)
    ref_digest = k.Keccak(msg, r, c, sfx, n)
    print('reference:', ref_digest)

    assert digest.upper() == ref_digest
    print('SUCCESS digest match')

    print('REFOUT message:', refout_msg)
    print('REFOUT digest :', refout_digest)
    print('SEED was:', seed)
    print(stats)

    import inspect
    report = {
        'seed': seed,
        'extra_seed': extra_seed,
        'message': (msg, mb),
        'digest': digest.upper(),
        'stats': stats,
        'msglen': msglen,
        'roundlimit': roundlimit,
        'msgbits': msgbits,
        'outbits': outbits,
        'branch:': inspect.getsourcelines(branch_order) if branch_order is not None else 'none'
    }
    with open('stats-sha3.dat', 'a') as f:
        f.write(str(report) + '\n')
    return report

if __name__ == '__main__':
    main()