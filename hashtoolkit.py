from instance import *
from hashes import *
import click
from subprocess import Popen, PIPE, call
import optimizers
import random

hash_functions = {
    'sha-1': {
        'rounds': 80,
        'output_len': 160,
        'functions': [
            SHA1_create_message,
            SHA1_run,
            SHA1_print_and_verify,
            SHA1_random_ref,
        ],
        'msgindex': (lambda i: (i//32, 31 - i%32)),
        'outindex': (lambda i: (i//32, 31 - i%32)),
    },
    'sha-3-512': {
        'rounds': 24,
        'output_len': 512,
        'functions': [
            SHA3_create_message,
            SHA3_run,
            SHA3_print_and_verify,
            SHA3_random_ref,
        ],
        'msgindex': (lambda i: (i//64, i%64)),
        'outindex': (lambda i: (i//64, i%64)),
    },
    'md5': {
        'rounds': 64,
        'output_len': 128,
        'functions': [
            MD5_create_message,
            MD5_run,
            MD5_print_and_verify,
            MD5_random_ref,
        ],
        'msgindex': (lambda i: (i//32, i%32)),
        'outindex': (lambda i: (i//32, i%32)),

    }
}

@click.command()
@click.option('--hash_name', '-h', default='sha1', help='Hash function to use, supported: ' + ', '.join(hash_functions.keys()))
@click.option('--message_len', '-l', default=8*8, help='Input message length in bits')
@click.option('--rounds', '-r', default=-1, help='Number of rounds, -1 for full')
@click.option('--input-fix', '-i', default='', help='Fix input bits, as 0/1 string')
@click.option('--output-fix', '-o', default='', help='Fix output bits, as 0/1/r string, where r is reference')
@click.option('--sat_cmd', '-c', default='minisat', help='Solver command to use')
@click.option('--seed', '-s', default=-1, help='Seed for random reference message')
@click.option('--collision', is_flag=True, default=False, help='Find collision instead of preimage, use -o with 0/1 to set which output bits should match')
@click.option('--out-file', '-f', default='', help='File for statistics output')
def main(hash_name, message_len, rounds, input_fix, output_fix, sat_cmd, seed, collision, out_file):
    run(hash_name, message_len, rounds, input_fix, output_fix, sat_cmd, seed, collision, out_file, out_file == '')

def run(hash_name, message_len, rounds, input_fix, output_fix, sat_cmd, seed, collision, out_file, use_call=False):
    if hash_name not in hash_functions:
        print('Unsupported hash function')
        return
    hash = hash_functions[hash_name]

    if rounds == -1:
        rounds = hash['rounds']

    instance = Instance()
    msg = hash['functions'][0](message_len)
    out = hash['functions'][1](msg, rounds)
    if collision:
        msg2 = hash['functions'][0](message_len)
        out2 = hash['functions'][1](msg2, rounds)
        # Make sure messages are not equal
        inor = ConstantVector([0]*32)
        for i in range(len(msg)):
            inor = inor | (msg[i] ^ msg2[i])
        allrots = ConstantVector([0]*32)
        for i in range(32):
            allrots = allrots | CyclicLeftShift(inor, i)
        allrots.bits[0] = True


    for i in range(len(msg)):
        msg[i].annotation = 'Message word #' + str(i)
    for i in range(len(out)):
        out[i].annotation = 'Output word #' + str(i)

    # Generate reference message
    if seed == -1:
        seed = random.randint(1, 2**32)
    random.seed(seed)
    refmsg, refdigest, refbits = hash['functions'][3](message_len, rounds)

    # Fix input bits
    for i in range(min(message_len, len(input_fix))):
        if input_fix[i] != '?':
            x, y = hash['msgindex'](i)
            msg[x].bits[y] = input_fix[i] == '1'
            if collision:
                msg2[x].bits[y] = input_fix[i] == '1'

    # Fix output bits if in preimage mode
    if not collision:
        for i in range(min(hash['output_len'], len(output_fix))):
            if output_fix[i] != '?':
                x, y = hash['outindex'](i)
                if output_fix[i] in ['0', '1']:
                    out[x].bits[y] = output_fix[i] == '1'
                else:
                    out[x].bits[y] = refbits[i]
    # Fix output xor bits if in collision mode
    else:
        outxor = []
        for i in range(len(out)):
            outxor.append(out[i] ^ out2[i])
        for i in range(min(hash['output_len'], len(output_fix))):
            if output_fix[i] != '?':
                x, y = hash['outindex'](i)
                outxor[x].bits[y] = output_fix[i] == '0'

    # Output and solve
    if collision:
        instance.emit(msg + out + outxor + [allrots])
    else:
        instance.emit(msg + out)

    if use_call:
        call([sat_cmd, 'instance.cnf', 'instance.out'])
        stdout = None
    else:
        p = Popen([sat_cmd, 'instance.cnf', 'instance.out'], stdout=PIPE)
        stdout, _ = p.communicate()
    instance.read('instance.out')

    # Verify and output

    print('Reference message:', refmsg, ' '*max(0, 22-len(str(refmsg))), 'Reference digest:', refdigest)
    print('Seed for repeatability:', seed)
    
    hash['functions'][2](instance, msg, out, message_len, rounds)
    if collision:
        hash['functions'][2](instance, msg2, out2, message_len, rounds)


    instance.write_annotations('annotations.dat')
    if stdout and out_file:
        time = None
        for line in stdout.decode().split('\n'):
            if line.strip().startswith('c Total time'):
                time = line.split(':')[1].strip()
                break
        if time is None:
            print('Could not find time')
            return
        with open(out_file, 'a') as f:
            # Write header
            if f.tell() == 0:
                f.write('rounds,time\n')
            f.write('{},{}\n'.format(rounds, time))
        print('Added record for rounds=', str(rounds), 'time=', time)

    return stdout

if __name__ == '__main__':
    main()