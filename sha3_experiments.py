import sha3_instance_test as sha3

sha3.msglen = 32
sha3.roundlimit = 16

sha3.outbits[:4] = ['ref']*4
#sha3.solver = ['./cmsrun.sh']
sha3.solver = ['minisat']

print(sha3.run_experiment(0))