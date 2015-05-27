from instance import *

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
# Big-endian bit list to int
def toIntBE(bits):
    return toInt(bits[::-1])

K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
   0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
   0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
   0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
   0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
   0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
   0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
   0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

Kvec = [intToVector(x) for x in K]

#################### CONFIGURATION ####################
# Original message length in bits
mlength = 0 # 16*8
# Number of rounds, full SHA256 is 64
rounds = 64

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

# Extend message to 64 32-bit words
for i in range(16, 64):
    s0 = CyclicLeftShift(Mvec[i-15], -7) ^ CyclicLeftShift(Mvec[i-15], -18) ^ LeftShift(Mvec[i-15], -3)
    s1 = CyclicLeftShift(Mvec[i-2], -17) ^ CyclicLeftShift(Mvec[i-2], -19) ^ LeftShift(Mvec[i-2], -10)
    Mvec.append(Mvec[i-16] + s0 + Mvec[i-7] + s1)
    #Mvec.append(BitVector(32))
    #Mvec.append(CyclicLeftShift(Mvec[i-3] ^ Mvec[i-8] ^ Mvec[i-14] ^ Mvec[i-16], 1))

h0, h1, h2, h3, h4, h5, h6, h7 = [intToVector(x) for x in [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]]

A, B, C, D, E, F, G, H = h0, h1, h2, h3, h4, h5, h6, h7
for i in range(rounds):
    S1 = CyclicLeftShift(E, -6) ^ CyclicLeftShift(E, -11) ^ CyclicLeftShift(E, -25)
    ch = (E & F) ^ ((~E) & G)
    temp1 = H + S1 + ch + Kvec[i] + Mvec[i]
    S0 = CyclicLeftShift(A, -2) ^ CyclicLeftShift(A, -13) ^ CyclicLeftShift(A, -22)
    maj = (A & B) ^ (A & C) ^ (B & C)
    temp2 = S0 + maj
    H = G
    G = F
    F = E
    E = D + temp1
    D = C
    C = B
    B = A
    A = temp1 + temp2
    #F = fs[i//20](A, B, C, D, E)
    #k = Kvec[i//20]
    #
    #T = CyclicLeftShift(A, 5) + F + E + k + Mvec[i]
    #A, B, C, D, E = T, A, CyclicLeftShift(B, 30), C, D
h0, h1, h2, h3, h4, h5, h6, h7 = h0+A, h1+B, h2+C, h3+D, h4+E, h5+F, h6+G, h7+H

#################### CONFIGURATION ####################
# Fix message/output bits here

#Mvec[0].bits = [True]*32
#h4.bits = [False]*8 + [None]*24

#######################################################

# TODO prettier
# Generate CNF instance, solve, read
print('Emit start')
instance.emit([h0, h1, h2, h3, h4] + Mvec)# + [QQ])
from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
instance.read('instance.out')

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

def digest_to_hex(digest):
    return '{:032x}'.format(int.from_bytes(digest, byteorder='little'))

from hashlib import sha256
sha = sha256()
sha.update(message)
reference = sha.digest()
print('sha256  ', reference, '  ', digest_to_hex(reference))
assert reference == toInt(Dbits)
print('MATCH!')