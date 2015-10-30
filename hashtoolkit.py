from instance import *
from hashes import *
import click
from subprocess import call

hash_functions = {
    'sha1': {
        'rounds': 80,
        'functions': [
            SHA1_create_message,
            SHA1_run,
            SHA1_print_and_verify,
        ]
    },
    'md5': {
        'rounds': 64,
        'functions': [
            MD5_create_message,
            MD5_run,
            MD5_print_and_verify,
        ]
    }
}

@click.command()
@click.option('--hash_name', '-h', default='sha1')
@click.option('--message_len', '-l', default=8*8)
@click.option('--rounds', '-r', default=-1)
@click.option('--sat_cmd', '-s', default='minisat')
def main(hash_name, message_len, rounds, sat_cmd):
    if hash_name not in hash_functions:
        print('Unsupported hash function')
        return
    hash = hash_functions[hash_name]

    if rounds == -1:
        rounds = hash['rounds']

    instance = Instance()
    msg = hash['functions'][0](message_len)
    out = hash['functions'][1](msg, rounds)

    instance.emit(msg + out)
    call([sat_cmd, 'instance.cnf', 'instance.out'])
    instance.read('instance.out')

    hash['functions'][2](instance, msg, out, message_len, rounds)

if __name__ == '__main__':
    main()