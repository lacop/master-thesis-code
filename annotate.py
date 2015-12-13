import os
_, _, files = list(os.walk('confls/'))[0]
import pickle

data = pickle.load(open('annotations.dat', 'rb'))

for file in files:
    f = open('confls/' + file)
    lines = f.readlines()
    f.close()
    f = open('confls/' + file, 'w')
    for line in lines:
        if 'shape="box"' in line:
            var = line.split()[0].strip()
            if var[0] == 'x' and var[1:].isnumeric():
                var = int(var[1:])
                line = line[:line.find('" ];')]
                line += '\\n'
                line += data[var]
                line += '" ];\n'
        f.write(line)
    f.close()
