# Test MD5 implementation from scratch

# Constants
S = [ 7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
      5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
      4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
      6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21]
K = [0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
     0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
     0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
     0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
     0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
     0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
     0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
     0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
     0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
     0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
     0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
     0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
     0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
     0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
     0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
     0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]

fs = [lambda a, b, c, d: (b & c) | (~b & d),
      lambda a, b, c, d: (d & b) | (~d & c),
      lambda a, b, c, d: b ^ c ^ d,
      lambda a, b, c, d: c ^ (b | ~d)]
gs = [lambda i: i,
      lambda i: (5*i + 1) % 16,
      lambda i: (3*i + 5) % 16,
      lambda i: (7*i) % 16,]

def leftrotate(x, i):
    #print('rot', x, i)
    return ((x << i) | (x >> (32 - i))) & 0xFFFFFFFF

def md5(message, rounds = 64):
    a0 = 0x67452301
    b0 = 0xefcdab89
    c0 = 0x98badcfe
    d0 = 0x10325476

    message = bytearray(message)
    length = 8 * len(message)

    # Append 1
    message.append(0b10000000)

    # Append zeroes to pad
    while len(message) % 64 != 56:
        message.append(0)
    # Append original length
    message += length.to_bytes(8, byteorder='little')

    # Split to chunks of size 64 bytes
    for pos in range(0, len(message), 64):
        chunk = message[pos:pos+64]

        A, B, C, D = a0, b0, c0, d0
        for i in range(rounds):
            F = fs[i//16](A, B, C, D)
            G = gs[i//16](i)

            mg = int.from_bytes(chunk[4*G:4*G+4], byteorder='little')
            rot = leftrotate((A + F + K[i] + mg) & 0xFFFFFFFF, S[i])

            A, B, C, D = D, (B+rot) & 0xFFFFFFFF, B, C

        a0 = (a0 + A) & 0xFFFFFFFF
        b0 = (b0 + B) & 0xFFFFFFFF
        c0 = (c0 + C) & 0xFFFFFFFF
        d0 = (d0 + D) & 0xFFFFFFFF
    digest = 0
    for x in [d0, c0, b0, a0]:
        digest = digest<<32 | x
    return digest


def digest_to_hex(digest):
    return '{:032x}'.format(int.from_bytes(digest.to_bytes(16, byteorder='little'), byteorder='big'))

if __name__ == '__main__':
    assert digest_to_hex(md5(b'')) == 'd41d8cd98f00b204e9800998ecf8427e'
    assert digest_to_hex(md5(b'The quick brown fox jumps over the lazy dog')) == '9e107d9d372bb6826bd81d3542a419d6'
    assert digest_to_hex(md5(b'The quick brown fox jumps over the lazy dog.')) == 'e4d909c290d0fb1ca068ffaddf22cbd0'
    print(digest_to_hex(md5(b'')))
    print(md5(b""))