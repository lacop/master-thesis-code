from instance import *
from sha3_reference import Keccak

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

##########

# TODO flexible, these are sha3-512 settings
r = 576
n = 512
c = 1024
nr = 24
sfx = 0x06
w = 64 # TODO

msglen = 8 # In bits

# Initial empty state
S = [[intToVector(0, 64) for _ in range(5)] for _ in range(5)]

# TODO support longer messages (multiple vectors)
P = [BitVector(64)]
spos = msglen
while sfx != 1:
    # TODO support when suffix needs to go to new vector
    P[-1].bits[spos] = sfx % 2
    sfx //= 2
    spos += 1

# TODO proper padding
P[-1].bits[spos] = True
spos += 1
while spos < w:
    P[-1].bits[spos] = False
    spos += 1
for _ in range(7):
    P.append(intToVector(0, 64))
P.append(intToVector(9223372036854775808, 64))

def rounds():
    global S
    for i in range(nr):
        rc = intToVector(Keccak.RC[i], 64)
        B = [[intToVector(0, 64) for _ in range(5)] for _ in range(5)]
        C = [intToVector(0, 64) for _ in range(5)]
        D = [intToVector(0, 64) for _ in range(5)]

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

# Absorb
for i in range(len(P)*64//r):
    print(i)
    # TODO get from blok of P
    #pi = [[6, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 9223372036854775808, 0, 0, 0], [0, 0, 0, 0, 0]]
    #PP = P + '00'*(c//8)
    for y in range(5):
        for x in range(5):
            #S[x][y] = S[x][y] ^ intToVector(pi[x][y], 64)
            #q = int(PP[2*((5*y+x)*w)//8:][:2*w//8], 16)
            #S[x][y] = S[x][y] ^ intToVector(q, 64)
            idx = 5*y + x
            if idx < len(P):
                S[x][y] = S[x][y] ^ P[idx]
            #if not q == pi[x][y]:
            #    print(q, pi[x][y])
            #    print(x,y)
            #    print(PP[2*((5*y+x)*w)//8:][:2*w//8])
            #    assert False
    rounds()

# Squeeze
# TODO variable length output, bitrate output only, do rounds inbetween
out = []
for y in range(5):
    for x in range(5):
        out.append(S[x][y])

# Input message fixing
P[0].bits[:8] = [False, False, False, True, True, True, False, False] #0x38

# SOLVE
#rel = []
#for y in range(5):
#    for x in range(5):
#        rel.append(S[x][y])
#instance.emit(rel)
instance.emit(out + P)
from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
instance.read('instance.out')

# Test
print(P[i].getValuation(instance)[:msglen])
print(toInt(P[i].getValuation(instance)[:msglen]))
print(toHexInt(P[i].getValuation(instance)[:msglen]))
for i in range(len(P)):
    print(i, toHexInt(P[i].getValuation(instance)))
#    print(i, toHexInt(P[i].getValuation(instance)), toInt(P[i].getValuation(instance)), P[i].getValuation(instance))

for y in range(5):
    for x in range(5):
        print(toHexInt(S[x][y].getValuation(instance)), '\t', end='')
    print()

# Output/verify
digest = ''
for q in out:
    dx = toHexInt(q.getValuation(instance))[2:]
    for i in range(len(dx)//2):
        digest += dx[-2*(i+1):][:2]
digest = digest[:2*n//8]
print(digest)

#assert digest.upper() == 'A69F73CCA23A9AC5C8B567DC185A756E97C982164FE25859E0D1DCC1475C80A615B2123AF1F5F94C11E3E9402C3AC558F500199D95B6D3E301758586281DCD26'
assert digest.upper() == 'F30E8484FA863883156C517514C4E2A9096EC6009F40EBFB9F00666EC58E52E50E64F9074C9182A325A21CC99516B155560F8C48BE28F11F2EE73F6945FF7563'
print('SUCCESS digest match')