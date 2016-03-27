import sha3_instance_test as sha3

# sha3.msglen = 32
# sha3.roundlimit = 6
#
# sha3.outbits[:8] = ['ref']*8
# #sha3.solver = ['./cmsrun.sh']
# #sha3.solver = ['minisat']
# sha3.solver = ['./minisatrun.sh']
#
# def bo(i, rv):
#     for rnd in [5]:
#         #X, Y -> S[x][y]
#         for x in range(5):
#             for y in range(5):
#                 i.branch(rv[rnd][0][x][y].vars) # S
#
# print(sha3.run_experiment(0, bo)['stats'])


def multiple_runs(csvfile, msglen, rounds, outrefcnt, solver, bo, bodesc, seeds):
    sha3.msglen = msglen
    sha3.roundlimit = rounds
    sha3.outbits[:outrefcnt] = ['ref']*outrefcnt
    sha3.solver = solver

    warn = False
    for i in range(seeds):
        print('Run', i+1, 'out of', seeds)
        report = sha3.run_experiment(i, bo)
        if report is None:
            warn = True
            print('WARNING: unsatisfiable or timed out')
            report = {'stats': {'conflicts': -1, 'time': '?'}}
        with open(csvfile, 'a') as f:
            f.write(','.join([
                str(msglen), str(rounds), str(outrefcnt),
                '[' + ' '.join(solver) + ']',
                bodesc,
                str(i),
                str(report['stats']['conflicts']), report['stats']['time']
            ]) + '\n')
    if warn:
        print('WARNING: ONE OR MORE RUNS DID NOT FINISH PROPERLY')

def genbo(order):
    def bo(i, rv):
        for sel in order:
            i.branch(sel(rv).vars)
    return bo

def experiment_1():
    # SHA3, message length = 32, preimage = 8bit reference
    # Different number of rounds
    # Test with different branch orders
    # Multiple runs each (10 different seeds x 10 tries = 100 total)
    # Timeout = 60s

    branch_orders = {
        'none': None,
        'r0-S-x-y': genbo([lambda rv: rv[0][0][x][y] for x in range(5) for y in range(5)]),
        'r0-S-y-x': genbo([lambda rv: rv[0][0][x][y] for y in range(5) for x in range(5)]),
        'rlast-S-x-y': genbo([lambda rv: rv[-1][0][x][y] for x in range(5) for y in range(5)]),
        'rlast-S-y-x': genbo([lambda rv: rv[-1][0][x][y] for y in range(5) for x in range(5)]),
    }

    for _ in range(10):
        for rounds in range(1, 25):
            for bodesc, bo in branch_orders.items():
                print('Rounds=', rounds, 'BO=', bodesc)
                multiple_runs(
                    'experiments/ex1-sha3-minisat-bos.csv',
                    32, rounds, 8,
                    ['timeout', '60', './minisatrun.sh'],
                    bo, bodesc,
                    10)
#experiment_1()

def experiment_2():
    # SHA3, message length = 32, preimage = 4bit reference
    # Different number of rounds
    # Test with different branch orders (more than ex1)
    # Multiple runs each (5 different seeds x 2 tries = 10 total)
    # Timeout = 60s

    branch_orders = {
        'none': None,
        'r0-S-x-y': genbo([lambda rv: rv[0][0][x][y] for x in range(5) for y in range(5)]),
        'r0-S-y-x': genbo([lambda rv: rv[0][0][x][y] for y in range(5) for x in range(5)]),
        'r1-S-x-y': genbo([lambda rv: rv[1][0][x][y] for x in range(5) for y in range(5)]),
        'r1-S-y-x': genbo([lambda rv: rv[1][0][x][y] for y in range(5) for x in range(5)]),
        'rlast-S-x-y': genbo([lambda rv: rv[-1][0][x][y] for x in range(5) for y in range(5)]),
        'rlast-S-y-x': genbo([lambda rv: rv[-1][0][x][y] for y in range(5) for x in range(5)]),
        'r0-B-x-y': genbo([lambda rv: rv[0][1][x][y] for x in range(5) for y in range(5)]),
        'r0-B-y-x': genbo([lambda rv: rv[0][1][x][y] for y in range(5) for x in range(5)]),
        'r0-B-x-y': genbo([lambda rv: rv[0][1][x][y] for x in range(5) for y in range(5)]),
        'r0-B-y-x': genbo([lambda rv: rv[0][1][x][y] for y in range(5) for x in range(5)]),
        'r0-C-x': genbo([lambda rv: rv[0][2][x] for x in range(5)]),
        'r0-D-x': genbo([lambda rv: rv[0][3][x] for x in range(5)]),
    }

    for _ in range(2):
        for rounds in range(2, 25): # Start from 2
            for bodesc, bo in branch_orders.items():
                print('Rounds=', rounds, 'BO=', bodesc)
                multiple_runs(
                    'experiments/ex2-sha3-minisat-bos.csv',
                    32, rounds, 8,
                    ['timeout', '60', './minisatrun.sh'],
                    bo, bodesc,
                    5)
experiment_2()

# multiple_runs('experiments/tmp.csv',
#               32, 24, 4,
#               ['timeout', '30', './minisatrun.sh'],
#               #genbo([lambda rv: rv[0][0][x][y] for x in range(5) for y in range(5)]), 'r0-S-x-y',
#               genbo([lambda rv: rv[1][0][x][y] for x in range(5) for y in range(5)]), 'r1-S-x-y',
#               #None, 'none',
#               1)