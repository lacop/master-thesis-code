from hashtoolkit import run

PLOTDIR = 'plots/'

def genXYplot(name, xlabel, ylabel, xvals, multi, fnc):
    fa = open(PLOTDIR + name + '.gnuplot', 'w')
    fb = open(PLOTDIR + name + '-tex.gnuplot', 'w')
    fa.write('set terminal x11 persist\n')
    fb.write('set terminal epslatex color lw 2 solid\n')

    def w(str):
        fa.write(str)
        fb.write(str)

    w('set size 1.0, 1.0\n')
    w('set xlabel "'+ xlabel + '"\n')
    w('set ylabel "' + ylabel + '"\n')

    fb.write('set output "' + PLOTDIR + name + '.eps" \n')

    if multi is None:
        w('plot "' + PLOTDIR + name + '.dat" using 1:2 title "' + name +'" with lines\n')
    else:
        w('plot ')
        first = True
        for m in multi:
            if not first:
                w(', \\\n     ')
            # TODO tuples
            #n = '-'.join([str(x) for x in m])
            n = str(m)
            w('"' + PLOTDIR + name + '-' + n + '.dat" using 1:2 title "' + n +'" with lines')
            first = False
    fa.close()
    fb.close()


    # TODO call cashing
    if multi is None:
        f = open(PLOTDIR + name + '.dat', 'w')
        for x in xvals:
            y = fnc(x)
            f.write(str(x) + ' ' + str(y) + '\n')
            print(x, y)
        f.close()
    else:
        for m in multi:
            #n = '-'.join([str(x) for x in m])
            n = str(m)
            f = open(PLOTDIR + name + '-' + n + '.dat', 'w')
            for x in xvals:
                y = fnc(m, x)
                f.write(str(x) + ' ' + str(y) + '\n')
                print(x, y)
            f.close()


def getStats(output):
    lines = output.decode('utf-8').split('\n')

    cputime = [l for l in lines if l.startswith('CPU')][0].split(':')[1].strip()[:-2]

    return {
        'time': cputime,
    }

#genXYplot('test', range(1, 100), lambda x: x**2)

# genXYplot('sha1-input64-out4fixed-rounds',
#           'Rounds', 'Time [s]',
#           range(1, 80), None,
#           lambda x: getStats(run(
#               hash_name='sha1',
#               message_len=64,
#               rounds = x,
#               input_fix='',
#               output_fix='1111',
#               sat_cmd='minisat'
#           ))['time'])

# genXYplot('sha1-input64-out8fixed-rounds',
#           'Rounds', 'Time [s]',
#           range(1, 80), None,
#           lambda x: getStats(run(
#               hash_name='sha1',
#               message_len=64,
#               rounds = x,
#               input_fix='',
#               output_fix='11111111',
#               sat_cmd='minisat'
#           ))['time'])

genXYplot('sha1-input64-out16fixed-rounds',
          'Rounds', 'Time [s]',
          range(1, 80), None,
          lambda x: getStats(run(
              hash_name='sha1',
              message_len=64,
              rounds = x,
              input_fix='',
              output_fix='1111111111111111',
              sat_cmd='minisat'
          ))['time'])

# genXYplot('sha1-input64-multiround-outfixed',
#           'Rounds', 'Time [s]',
#           range(1, 16), [1, 5, 10, 15],
#           lambda r, x: getStats(run(
#               hash_name='sha1',
#               message_len=64,
#               rounds = r,
#               input_fix='',
#               output_fix='1'*x,
#               sat_cmd='minisat'
#           ))['time'])