#!/bin/bash

rm *.hpf

black .
flake8 --config flake8.cfg
python3 -m unittest -v

for f in build dist *.egg-info; do 
    echo remove $f
    rm $f -rf
done

find . -name __pycache__ | xargs rm -rf  
