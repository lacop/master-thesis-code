#!/bin/bash

#/home/lacop/Projects/cryptominisat/cryptominisat4 $1 | tee $2
/home/lacop/Projects/cryptominisat/cryptominisat4 $1 | tee $2 | grep '^c\|^s'
#/home/lacop/Projects/cryptominisat/cryptominisat4 $1 > $2

