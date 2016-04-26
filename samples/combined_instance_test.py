import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
from library.instance import *
from hashes import *

instance = Instance()

#mlength = 8*48
mlength = 8*16
md5rounds = 16 #64
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
outxor[0].bits = [False]*32 + [None]*0
#outxor[-1].bits = [None]*6 + [False]*24
#for i in range(len(outxor)):
#    outxor[i].bits = [False]*32

inor = ConstantVector([0]*32)
for i in range(len(md5msg)):
    inor = inor | (md5msg[i] ^ md5msg2[i])
#inor.bits = [True]*16 + [None]*16
allrots = ConstantVector([0]*32)
for i in range(32):
    allrots = allrots | CyclicLeftShift(inor, i)
allrots.bits[0] = True

instance.emit(md5msg + md5out + md5msg2 + md5out2 + outxor + [allrots])
#instance.emit(sh1msg + sha1out)

from subprocess import call
call(['minisat', 'instance.cnf', 'instance.out'])
instance.read('instance.out')

MD5_print_and_verify(instance, md5msg, md5out, mlength, md5rounds)
MD5_print_and_verify(instance, md5msg2, md5out2, mlength, md5rounds)
#SHA1_print_and_verify(instance, sha1msg, sha1out, mlength, sha1rounds)