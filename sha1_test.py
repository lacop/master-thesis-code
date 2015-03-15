# Test MD5 implementation from scratch

# Constants
fs = [lambda a, b, c, d, e: (b & c) | (~b & d),
      lambda a, b, c, d, e: b ^ c ^ d,
      lambda a, b, c, d, e: (b & c) | (b & d) | (c & d),
      lambda a, b, c, d, e: b ^ c ^ d]
K = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6]
def leftrotate(x, i):
    #print('rot', x, i)
    return ((x << i) | (x >> (32 - i))) & 0xFFFFFFFF

def sha1(message, rounds = 80):
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0

    message = bytearray(message)
    length = 8 * len(message)

    # Append 1
    message.append(0b10000000)

    # Append zeroes to pad
    while len(message) % 64 != 56:
        message.append(0)
    # Append original length
    message += length.to_bytes(8, byteorder='big')


    #print(len(message))
    # Split to chunks of size 64 bytes
    for pos in range(0, len(message), 64):
        chunk = message[pos:pos+64]

        W = [int.from_bytes(chunk[4*i:4*i+4], byteorder='big') for i in range(16)]
        for i in range(16, 80):
            W.append(leftrotate(W[i-3] ^ W[i-8] ^ W[i-14] ^ W[i-16], 1))

        #print(W)
        A, B, C, D, E = h0, h1, h2, h3, h4
        for i in range(rounds):
            F = fs[i//20](A, B, C, D, E)
            k = K[i//20]

            T = (leftrotate(A, 5) + F + E + k + W[i]) & 0xFFFFFFFF
            E = D
            D = C
            C = leftrotate(B, 30)
            B = A
            A = T
            #mg = int.from_bytes(chunk[4*G:4*G+4], byteorder='little')
            #rot = leftrotate((A + F + K[i] + mg) & 0xFFFFFFFF, S[i])
            #print((A + F + K[i] + mg) & 0xFFFFFFFF, rot)
            #A, B, C, D = D, (B+rot) & 0xFFFFFFFF, B, C
            #print(A)
            #print(B)
            #print(C)
            #print(D)
        h0 = (h0 + A) & 0xFFFFFFFF
        h1 = (h1 + B) & 0xFFFFFFFF
        h2 = (h2 + C) & 0xFFFFFFFF
        h3 = (h3 + D) & 0xFFFFFFFF
        h4 = (h4 + E) & 0xFFFFFFFF
        #print(a0)
        #print(b0)
        #print(c0)
        #print(d0)
    digest = 0
    for x in [h0, h1, h2, h3, h4]:
        digest = digest<<32 | x
    return digest


def digest_to_hex(digest):
    return '{:032x}'.format(digest)

if __name__ == '__main__':
    assert digest_to_hex(sha1(b'')) == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    assert digest_to_hex(sha1(b'The quick brown fox jumps over the lazy dog')) == '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12'
    assert digest_to_hex(sha1(b'The quick brown fox jumps over the lazy cog')) == 'de9f2c7fd25e1b3afad3e85a0bd17d9b100db4b3'

    print(digest_to_hex(sha1(b'')))