#!/usr/bin/env bash

for i in $(ip link show | sed -nre 's/[0-9]+: (.+?): .*/\1/p'); do

    if [ "${i}" == "lo" ]; then
        continue
    fi
    mkdir "${i}"
    cp Vagrantfile "${i}"
    cp -r .vagrant "${i}"
    cd "${i}"
    sed -i -- 's/sys/..\/sys/g' Vagrantfile
    sed -i -- 's/auto_config:\ false/bridge:\ \"'$i'\"/g' Vagrantfile
    vagrant reload
    cd ..

done

