#for rnds in `seq 80 -1 0`;
for i in `seq 100`;
do
    for rnds in `seq 0 80`;
    do
        echo "ROUNDS" $rnds "REP" $i
        #python3 hashtoolkit.py -h sha1 -l 32 -r $rnds -o 'rrrrrrrrrrrr' -s './cmsrunq.sh' -f r-tests/sha1-32bit-out12bitREF.csv
        python3 hashtoolkit.py -h sha1 -l 32 -r $rnds -o 'rrrrrrrr' -s './cmsrunq.sh' -f 'r-tests/sha1-32bit-out8bitREF.csv'
    done
done
