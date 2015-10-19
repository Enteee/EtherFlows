#!/usr/bin/env bash

# Enable all network interfaces
for i in $(ip link show | sed -nre 's/[0-9]+: (.+?): .*/\1/p'); do
    ip link set dev "${i}" up
done
