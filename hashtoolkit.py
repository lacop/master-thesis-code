from instance import *
from hashes import *
import click
from subprocess import Popen, PIPE, call
import optimizers

hash_functions = {
    'sha1': {
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
    'md5': {
        'rounds': 64,
        'output_len': 128,
        'functions': [
            MD5_create_message,
            MD5_run,
            MD5_print_and_verify,
        ],
        'msgindex': (lambda i: (i//32, i%32)),
        'outindex': (lambda i: (i//32, i%32)),

    }
}

@click.command()
@click.option('--hash_name', '-h', default='sha1')
@click.option('--message_len', '-l', default=8*8)
@click.option('--rounds', '-r', default=-1)
@click.option('--input-fix', '-i', default='')
@click.option('--output-fix', '-o', default='')
@click.option('--sat_cmd', '-s', default='minisat')
def main(hash_name, message_len, rounds, input_fix, output_fix, sat_cmd):
    run(hash_name, message_len, rounds, input_fix, output_fix, sat_cmd, True)

def run(hash_name, message_len, rounds, input_fix, output_fix, sat_cmd, use_call=False):
    if hash_name not in hash_functions:
        print('Unsupported hash function')
        return
    hash = hash_functions[hash_name]

    if rounds == -1:
        rounds = hash['rounds']

    instance = Instance()
    msg = hash['functions'][0](message_len)
    out = hash['functions'][1](msg, rounds)

    for i in range(len(msg)):
        msg[i].annotation = 'Message word #' + str(i)
    for i in range(len(out)):
        out[i].annotation = 'Output word #' + str(i)

    # TODO fixable seed for reference message?
    refmsg, refdigest, refbits = hash['functions'][3](message_len, rounds)
    for i in range(min(message_len, len(input_fix))):
        if input_fix[i] != '?':
            x, y = hash['msgindex'](i)
            msg[x].bits[y] = input_fix[i] == '1'
    for i in range(min(hash['output_len'], len(output_fix))):
        if output_fix[i] != '?':
            x, y = hash['outindex'](i)
            if output_fix[i] in ['0', '1']:
                out[x].bits[y] = output_fix[i] == '1'
            else:
                out[x].bits[y] = refbits[i]

    # TODO merge xor clauses / other optimizations

    instance.emit(msg + out)
    if use_call:
        call([sat_cmd, 'instance.cnf', 'instance.out'])
        stdout = None
    else:
        p = Popen([sat_cmd, 'instance.cnf', 'instance.out'], stdout=PIPE)
        stdout, _ = p.communicate()
    instance.read('instance.out')

    print('Reference message:', refmsg, ' '*max(0, 22-len(str(refmsg))), 'Reference digest:', refdigest)

    hash['functions'][2](instance, msg, out, message_len, rounds)
    instance.write_annotations('annotations.dat')

    return stdout

if __name__ == '__main__':
    main()