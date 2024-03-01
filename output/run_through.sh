#!/usr/bin/env bash

for i in $(seq $1 $2); do
python algo2.py $i $3 $4 &
done

wait
echo "Finished!"
