from instance import *
import md5_test
import sha1_test
import random
from optimizers import OptimizeExpression

def intToVector(x, size=32):
    bits = [False]*size
    i = 0
    while x > 0:
        bits[i] = (x % 2 == 1)
        i += 1
        x //= 2
    vec = ConstantVector(bits)
    vec.annotation = 'Constant vector ' + str(x)
    return vec
# Little-endian bit list to int
def toInt(bits):
    val = 0
    for b in bits[::-1]:
        val = val*2 + (1 if b else 0)
    return val

def MD5_create_message(mlength):
    Mvec = [BitVector(32) for _ in range(14)]

    # Padding - "1", then "0" until 448 bits
    for i in range(mlength, 448):
        Mvec[i // 32].bits[i % 32] = True if i == (mlength + 7) else False
    # Length in the last 64 bits, little endian
    Mvec.append(intToVector(mlength % (2**32)))
    Mvec.append(intToVector(mlength // (2**32)))

    return Mvec

def MD5_run(message, rounds):
    Kvec = [intToVector(x) for x in md5_test.K]
    a0, b0, c0, d0 = [intToVector(x) for x in [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]]
    A, B, C, D = a0, b0, c0, d0
    for i in range(rounds):
        F = md5_test.fs[i//16](A, B, C, D)
        G = md5_test.gs[i//16](i)

        X = A + F + Kvec[i] + message[G]
        R = CyclicLeftShift(X, md5_test.S[i])

        A, B, C, D = D, B+R, B, C
    a0, b0, c0, d0 = a0+A, b0+B, c0+C, d0+D
    return [a0, b0, c0, d0]

def MD5_print_and_verify(instance, Mvec, digest, mlength, rounds):
    # Get message bits
    Mbits = []
    for i in range(mlength):
        Mbits.append(Mvec[i // 32].getValuation(instance)[i % 32])
    print('Message length', mlength, 'bits') #, Mbits)
    # Get digest bits
    Dbits = []
    for q in digest:
        Dbits += q.getValuation(instance)
    print('Digest', toInt(Dbits)) #, Dbits)

    # Assume 8bit multiple length, generate message
    # Then test with reference implementation for match
    message = b""
    for i in range(0, mlength//8):
        bits = Mvec[i//4].getValuation(instance)[(i%4)*8 : (i%4)*8 + 8]
        message += toInt(bits).to_bytes(1, byteorder='little')
    print ('Message bytes:', message, 'rounds: ', rounds)

    reference = md5_test.md5(message, rounds=rounds)
    print('MD5   ', reference, md5_test.digest_to_hex(reference).zfill(32))
    assert reference == toInt(Dbits)
    print('MATCH!')

def MD5_random_ref(mlength, rounds):
    assert mlength % 8 == 0

    msg = bytes([random.randint(0, 255) for _ in range(mlength//8)])
    ref = md5_test.md5(msg, rounds=rounds)
    digest = md5_test.digest_to_hex(ref)

    bits = []
    while ref > 0 or len(bits) < 128:
        bits.append(ref % 2 == 1)
        ref //= 2
    return msg,digest,bits


# TODO generalize, annotate all hash functions

def SHA1_create_message(mlength):
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
        Mvec.append(CyclicLeftShift(Mvec[i-3] ^ Mvec[i-8] ^ Mvec[i-14] ^ Mvec[i-16], 1))

    return Mvec

def SHA1_run(message, rounds, optimized=False):
    Kvec = [intToVector(x) for x in sha1_test.K]

    h0, h1, h2, h3, h4 = [intToVector(x) for x in [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]]

    r1 = OptimizeExpression(lambda b, c, d: (b & c) ^ (~b & d))
    r24 = lambda b, c, d: b^c^d
    r3 = OptimizeExpression(lambda b, c, d: (b & c) ^ (b & d) ^ (c & d))
    opt_fs = [lambda a, b, c, d, e: r1(b, c, d),
              lambda a, b, c, d, e: r24(b, c, d),
              lambda a, b, c, d, e: r3(b, c, d),
              lambda a, b, c, d, e: r24(b, c, d)]
    A, B, C, D, E = h0, h1, h2, h3, h4
    for i in range(rounds):
        if optimized:
            F = opt_fs[i//20](A, B, C, D, E)
        else:
            F = sha1_test.fs[i//20](A, B, C, D, E)
        k = Kvec[i//20]
        F.annotation = 'Round #'+str(i)+' round function F'

        T = CyclicLeftShift(A, 5) + F + E + k + message[i]
        T.annotation = 'Round #'+str(i)+' sum T'
        A, B, C, D, E = T, A, CyclicLeftShift(B, 30), C, D
        A.annotation = 'Round #'+str(i)+' output A'
        B.annotation = 'Round #'+str(i)+' output B'
        C.annotation = 'Round #'+str(i)+' output C'
        D.annotation = 'Round #'+str(i)+' output D'
        E.annotation = 'Round #'+str(i)+' output E'
    h0, h1, h2, h3, h4 = h0+A, h1+B, h2+C, h3+D, h4+E
    return [h0, h1, h2, h3, h4]

def SHA1_print_and_verify(instance, Mvec, digest, mlength, rounds):
    # Get message bits
    Mbits = []
    for i in range(mlength):
        Mbits.append(Mvec[i // 32].getValuation(instance)[31 - (i % 32)])
    print('Message length', mlength, 'bits')#, Mbits)

    # Get digest bits
    Dbits = []
    for q in digest[::-1]:
        Dbits += q.getValuation(instance)
    print('Digest', str(toInt(Dbits)).zfill(50)) #, Dbits)

    # Assume 8bit multiple length, generate message
    # Then test with reference implementation for match
    message = b""
    for i in range(0, mlength//8):
        bits = Mvec[i//4].getValuation(instance)[(3-(i%4))*8 : (3-(i%4))*8 + 8]
        message += toInt(bits).to_bytes(1, byteorder='big')
    print ('Message bytes:', message, 'rounds: ', rounds)

    reference = sha1_test.sha1(message, rounds=rounds)
    print('sha1  ', str(reference).zfill(50), '  ', sha1_test.digest_to_hex(reference))
    assert reference == toInt(Dbits)
    print('MATCH!')

def SHA1_random_ref(mlength, rounds):
    assert mlength % 8 == 0

    msg = bytes([random.randint(0, 255) for _ in range(mlength//8)])
    ref = sha1_test.sha1(msg, rounds=rounds)
    digest = sha1_test.digest_to_hex(ref)

    bits = []
    while ref > 0 or len(bits) < 160:
        bits.append(ref % 2 == 1)
        ref //= 2
    return msg,digest,bits[::-1]
