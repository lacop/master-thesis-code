from instance import *
from sha3_reference import Keccak
import math

instance = Instance()
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

##########

# Hash function configuration
#r, c, sfx, n = , , 0x06,  # SHA3-224
#r, c, sfx, n = 1088, 512, 0x06, 256 # SHA3-256
#r, c, sfx, n = , , 0x06,  # SHA3-384
r, c, sfx, n = 576, 1024, 0x06, 512 # SHA3-512
# TODO fix values ^ and make padding work with all
msglen = 32 # In bits
roundlimit = 8 # Max is 24

# Don't change
msgbits = [None]*msglen
outbits = [None]*n

# Message/digest bit config
#msgbits = [False, False, False, True, True, True, False, False] #0x38
#print(msgbits)
#outbits[:8] = [False]*8
#msgbits = []
#for i in range(msglen//8): # Printable ASCII
#    msgbits[i*8+7] = False
#    msgbits[i*8+6] = True


############

assert r%8 == 0
assert n%8 == 0
assert len(msgbits) == msglen

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

def rounds():
    global S, roundvars
    for i in range(roundlimit):
        rc = intToVector(Keccak.RC[i], 64) # TODO truncate to w bits
        B = [[intToVector(0, w) for _ in range(5)] for _ in range(5)]
        C = [intToVector(0, w) for _ in range(5)]
        D = [intToVector(0, w) for _ in range(5)]

        for x in range(5):
            C[x] = S[x][0] ^ S[x][1] ^ S[x][2] ^ S[x][3] ^ S[x][4]
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
                S[x][y] = B[x][y] ^ ((~B[(x+1)%5][y]) & B[(x+2)%5][y])

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

# Fix output bits
for i in range(n):
    nthbit(out, i, outbits[i])

# SOLVE
#rel = []
#for y in range(5):
#    for x in range(5):
#        rel.append(S[x][y])
#instance.emit(rel)
instance.assignVars(out + P)

#print(roundvars)

# branching order
for rnd in [1]:
    for x in range(5):
        for y in range(5):
            instance.branch(roundvars[rnd][0][x][y].vars) # S
            #instance.branch(roundvars[rnd][1][x][y].vars) # B
instance.emit(out + P)

#from subprocess import call
#call(['minisat', 'instance.cnf', 'instance.out'])
#instance.read('instance.out')
#stats = instance.solve('minisat')
stats = instance.solve('./cmsrun.sh')

# Test
#print(P[0].getValuation(instance)[:msglen])
#print(P[0].getValuation(instance)[msglen:])
#print(toInt(P[0].getValuation(instance)[:msglen]))
#print(toHexInt(P[0].getValuation(instance)[:msglen]))
#for i in range(len(P)):
#    print(i, toHexInt(P[i].getValuation(instance)))
#    print(i, toHexInt(P[i].getValuation(instance)), toInt(P[i].getValuation(instance)), P[i].getValuation(instance))

#for y in range(5):
#    for x in range(5):
#        print(toHexInt(S[x][y].getValuation(instance)), '\t', end='')
#    print()

# Output/verify
message = []
for i in range(msglen):
    message.append(P[i//w].getValuation(instance)[i%w])
print('message:', message)
msg = (msglen, bitsToHex(message))

mb = b''
for i in range(msglen//8):
    #mb += '-' + msg[1][2*i:2*i+2]
    #mb += '-' + '/'.join([str(x) for x in P[i//w].getValuation(instance)])
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

#assert digest.upper() == 'A69F73CCA23A9AC5C8B567DC185A756E97C982164FE25859E0D1DCC1475C80A615B2123AF1F5F94C11E3E9402C3AC558F500199D95B6D3E301758586281DCD26'
#assert digest.upper() == 'F30E8484FA863883156C517514C4E2A9096EC6009F40EBFB9F00666EC58E52E50E64F9074C9182A325A21CC99516B155560F8C48BE28F11F2EE73F6945FF7563'
