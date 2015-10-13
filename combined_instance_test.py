from instance import *
from hashes import *

instance = Instance()

mlength = 8*8
md5rounds = 64
sha1rounds = 80

md5msg = MD5_create_message(mlength)
md5out = MD5_run(md5msg, md5rounds)
#sha1msg = SHA1_create_message(mlength)
#sha1out = SHA1_run(sha1msg, sha1rounds)

md5msg2 = MD5_create_message(mlength)
md5out2 = MD5_run(md5msg2, md5rounds)

outxor = []
for i in range(len(md5out)):
    outxor.append(md5out[i] ^ md5out2[i])
outxor[0].bits = [False]*16 + [None]*16

instance.emit(md5msg + md5out + md5msg2 + md5out2 + outxor)
#instance.emit(sh1msg + sha1out)

from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
instance.read('instance.out')

MD5_print_and_verify(instance, md5msg, md5out, mlength, md5rounds)
MD5_print_and_verify(instance, md5msg2, md5out2, mlength, md5rounds)
#SHA1_print_and_verify(instance, sha1msg, sha1out, mlength, sha1rounds)