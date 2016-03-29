for i in `seq 100`;
do
    for rnds in `seq 80 -1 0`;
    do
        echo "ROUNDS" $rnds "REP" $i
        python3 hashtoolkit.py -h sha1 -l 32 -r $rnds -o 'rrrrrrrr' -s './cmsrunq.sh' -f r-tests/sha1-32bit-out8bitREF-espresso.csv
    done
done
