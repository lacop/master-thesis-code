from instance import *
from md5_test import S, K, fs, gs, md5

#print(md5(b"\x00", rounds=1))

instance = Instance()

# Everything is little endian
def intToVector(x, size=32):
    bits = [False]*size
    i = 0
    while x > 0:
        bits[i] = (x % 2 == 1)
        i += 1
        x //= 2
    return ConstantVector(bits)

Kvec = [intToVector(x) for x in K]

# Original message length in bits
mlength = 8*8
# For now just single block/chunk of 64bytes
# 14 block for data + padding, 2 block for length
# Total of 16 blocks
Mvec = [BitVector(32) for _ in range(14)]

# Padding - "1", then "0" until 448 bits
for i in range(mlength, 448):
    Mvec[i // 32].bits[i % 32] = True if i == (mlength + 7) else False
# Length in the last 64 bits, little endian
Mvec.append(intToVector(mlength % (2**32)))
Mvec.append(intToVector(mlength // (2**32)))

# Number of rounds, full MD5 is 64
rounds = 64

a0, b0, c0, d0 = [intToVector(x) for x in [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]]
A, B, C, D = a0, b0, c0, d0
for i in range(rounds):
    # TODO F / G
    F = fs[i//16](A, B, C, D)
    G = gs[i//16](i)

    X = A + F + Kvec[i] + Mvec[G]
    R = CyclicLeftShift(X, S[i])

    A, B, C, D = D, B+R, B, C
a0, b0, c0, d0 = a0+A, b0+B, c0+C, d0+D

# TODO prettier
# Generate CNF instance, solve, read
print('Emit start')
instance.emit([a0, b0, c0, d0] + Mvec)
from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
instance.read('instance.out')

# Little-endian bit list to int
def toInt(bits):
    val = 0
    for b in bits[::-1]:
        val = val*2 + (1 if b else 0)
    return val

# Get message bits
Mbits = []
for i in range(mlength):
    Mbits.append(Mvec[i // 32].getValuation(instance)[i % 32])
print('Message length', mlength, 'bits', Mbits)
# Get digest bits
Dbits = []
for q in [a0, b0, c0, d0]:
    Dbits += q.getValuation(instance)
print('Digest', toInt(Dbits)) #, Dbits)

# Assume 8bit multiple length, generate message
# Then test with reference implementation for match
message = b""
for i in range(0, mlength//8):
    bits = Mvec[i//4].getValuation(instance)[(i%4)*8 : (i%4)*8 + 8]
    message += toInt(bits).to_bytes(1, byteorder='little')
print ('Message bytes:', message)

reference = md5(message, rounds=rounds)
print('MD5   ', reference)
assert reference == toInt(Dbits)
print('MATCH!')