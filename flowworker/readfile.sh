#!/bin/bash

for f in ${*}; do
    fname=$(basename "${f}")
    if [ -f "${f}" ]; then
        echo "${fname}"
        tshark -r "${f}" -q -lT pdml | ~/EtherFlows/flowworker/flowworker.py -i "${fname}" -S -t 0 | nc -q 1 localhost 5000 -v
    fi
done

