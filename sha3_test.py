from sha3_reference import Keccak
k = Keccak()
if __name__ == '__main__':
    #assert k.Keccak((0, ''), 576, 1024, 0x06, 512, verbose=True) == 'A69F73CCA23A9AC5C8B567DC185A756E97C982164FE25859E0D1DCC1475C80A615B2123AF1F5F94C11E3E9402C3AC558F500199D95B6D3E301758586281DCD26'

    #print('\n', k.Keccak((8, 'FF'), 576, 1024, 0x06, 512, verbose=True))
    #print('\n', k.Keccak((8, '00'), 576, 1024, 0x06, 512, verbose=True))
    print('\n', k.Keccak((8, '38'), 576, 1024, 0x06, 512, verbose=True))