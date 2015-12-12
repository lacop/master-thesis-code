#!/bin/bash

/home/lacop/Projects/cryptominisat/cryptominisat4 --printimpldot 1 $1 | tee $2 | grep '^c\|^s'

