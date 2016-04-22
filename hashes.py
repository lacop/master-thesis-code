from instance import *
import md5_test
import sha1_test
import sha3_reference
import random, math
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

########################

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


########################

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

########################

# Return/set n-th bit of a list of words
def nthbit(L, n, value=None):
    i = n // len(L[0].bits)
    j = n % len(L[0].bits)
    if value is not None:
        L[i].bits[j] = value
        #print(value, i, j)
    else:
        return L[i].bits[j]

def SHA3_create_message(msglen):
    r, c, sfx, n, b, w, nr = 576, 1024, 0x06, 512, 1600, 64, 24 # SHA-3-512

    msgbits = [None]*msglen
    P = [BitVector(w) for _ in range(max(1, math.ceil(msglen / w)))]
    spos = 0
    while spos < msglen:
        nthbit(P, spos, msgbits[spos])
        spos += 1
    # Suffix
    sfxi = sfx
    while sfxi != 1:
        nthbit(P, spos, sfxi % 2)
        sfxi //= 2
        spos += 1
    # Padding
    nthbit(P, spos, True)
    spos += 1
    while spos < w:
        nthbit(P, spos, False)
        spos += 1
    for _ in range(7):
        P.append(intToVector(0, 64))
    P.append(intToVector(9223372036854775808, 64))

    return P

def SHA3_run(P, roundlimit):
    r, c, sfx, n, b, w, nr = 576, 1024, 0x06, 512, 1600, 64, 24 # SHA-3-512
    # Initial empty state
    S = [[intToVector(0, w) for _ in range(5)] for _ in range(5)]

    def rounds():
        #global S, roundvars
        for i in range(roundlimit):
            rc = intToVector(sha3_reference.Keccak.RC[i], 64) # TODO truncate to w bits
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
                    B[y][(2*x+3*y)%5] = CyclicLeftShift(S[x][y], sha3_reference.Keccak.r[x][y])

            for x in range(5):
                for y in range(5):
                    S[x][y] = B[x][y] ^ (~B[(x+1)%5][y] & B[(x+2)%5][y])

            S[0][0] = S[0][0] ^ rc

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
    out = []
    for y in range(5):
        for x in range(5):
            out.append(S[x][y])

    return out

def toHexInt(bits):
    return hex(toInt(bits))
def bitsToHex(bits):
    hex = ''
    for i in range(0, len(bits), 8):
        hex += ('00' + toHexInt(bits[i:i+8])[2:])[-2:]
    return hex

def SHA3_print_and_verify(instance, P, out, msglen, roundlimit):
    r, c, sfx, n, b, w, nr = 576, 1024, 0x06, 512, 1600, 64, 24 # SHA-3-512

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

def SHA3_random_ref(mlength, rounds):
    r, c, sfx, n, b, w, nr = 576, 1024, 0x06, 512, 1600, 64, 24 # SHA-3-512
    assert mlength % 8 == 0

    k = sha3_reference.Keccak(roundlimit=rounds)
    msg = bytes([random.randint(0, 255) for _ in range(mlength//8)])
    msg_bits = []
    for i in range(mlength):
        msg_bits.append(msg[i//8] & (1 << (i%8)))
    digest = k.Keccak((mlength, bitsToHex(msg_bits)), r, c, sfx, n)

    bits = [False]*n
    for i in range(n):
        bits[i] = int(digest[(i//8)*2:(i//8)*2 + 2], 16) & (1 << (i % 8))
    return msg,digest,bits
