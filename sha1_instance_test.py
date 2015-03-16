from instance import *
from sha1_test import K, fs, sha1, digest_to_hex

#print(digest_to_hex(sha1(b"", rounds=80)))
#print(sha1(b"", rounds=0))

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
#def intToVectorBE(x, size=32):
#    v = intToVector(x, size)
#    v.bits = v.bits[]
#    return v
# Little-endian bit list to int
def toInt(bits):
    val = 0
    for b in bits[::-1]:
        val = val*2 + (1 if b else 0)
    return val
def toIntBE(bits):
    return toInt(bits[::-1])


Kvec = [intToVector(x) for x in K]

# Original message length in bits
mlength = 8*4 # 8*1 #8*32

###################################################

# For now just single block/chunk of 64bytes,
# 14 blocks for data + padding, 2 blocks for length
# Total of 16 blocks
Mvec = [BitVector(32) for _ in range(14)]

# Padding - "1", then "0" until 448 bits
for i in range(mlength, 448):
    Mvec[i // 32].bits[31 - (i % 32)] = True if i == (mlength) else False

Mvec.append(intToVector(mlength // (2**32)))
Mvec.append(intToVector(mlength % (2**32)))

#print('    ', [toInt(v.bits) for v in Mvec])
#sha1(b'', rounds=0)
#assert False

# Extend message to 80 32-bit words
for i in range(16, 80):
    #Mvec.append(BitVector(32))
    Mvec.append(CyclicLeftShift(Mvec[i-3] ^ Mvec[i-8] ^ Mvec[i-14] ^ Mvec[i-16], 1))

#print('    ', [toInt(v.bits) for v in Mvec])
#sha1(b'\x00', rounds=0)
#assert False

# Number of rounds, full SHA1 is 80
rounds = 80 #16

#a0, b0, c0, d0 = [intToVector(x) for x in [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]]
h0, h1, h2, h3, h4 = [intToVector(x) for x in [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]]
#h0.bits = h0.bits[::-1]
#h1.bits = h1.bits[::-1]
#QQ = h0 + h1

A, B, C, D, E = h0, h1, h2, h3, h4
for i in range(rounds):
    F = fs[i//20](A, B, C, D, E)
    k = Kvec[i//20]

    T = CyclicLeftShift(A, 5) + F + E + k + Mvec[i]
    E = D
    D = C
    C = CyclicLeftShift(B, 30)
    B = A
    A = T
h0, h1, h2, h3, h4 = h0+A, h1+B, h2+C, h3+D, h4+E

###################################################

# Fix message/output bits here
#for i in range(8):
#    Mvec[0].bits[31-i] = False
#print(Mvec[0].bits)
#a0.bits = [True]*32

###################################################

# TODO prettier
# Generate CNF instance, solve, read
print('Emit start')
instance.emit([h0, h1, h2, h3, h4] + Mvec)# + [QQ])
from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
instance.read('instance.out')

#for q in [h0, h1, h2, h3, h4]:
#    print(toInt(q.getValuation(instance)))
#print(''.join(['1' if x else '0' for x in h0.getValuation(instance)]))
#print(''.join(['1' if x else '0' for x in h1.getValuation(instance)]))
#print(''.join(['1' if x else '0' for x in QQ.getValuation(instance)]))
#print(h1.getValuation(instance))
#print(QQ.getValuation(instance))
#print(toInt(h0.getValuation(instance)))
#print(toInt(h1.getValuation(instance)))
#print(toInt(QQ.getValuation(instance)))
#print(toInt(A.getValuation(instance)))
#print(toInt(B.getValuation(instance)))
#print(toInt(C.getValuation(instance)))
#print(toInt(D.getValuation(instance)))
#print(toInt(E.getValuation(instance)))
#print(toInt(Mvec[0].getValuation(instance)))
print('    ', [toInt(v.getValuation(instance)) for v in Mvec])
#assert False

# Get message bits
Mbits = []
for i in range(mlength):
    Mbits.append(Mvec[i // 32].getValuation(instance)[31 - (i % 32)])
print('Message length', mlength, 'bits')#, Mbits)
#print(Mvec[0].getValuation(instance))
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