import sha3_instance_test as sha3

sha3.msglen = 32
sha3.roundlimit = 12

sha3.outbits[:4] = ['ref']*4
#sha3.solver = ['./cmsrun.sh']
#sha3.solver = ['minisat']
sha3.solver = ['./minisatrun.sh']

def bo(i, rv):
    for rnd in []:
        #X, Y -> S[x][y]
        for x in range(5):
            for y in range(5):
                i.branch(rv[rnd][0][x][y].vars) # S

print(sha3.run_experiment(0, bo))