#!/bin/bash
FIRST=true
FLOWGEN_ID="0xBADA5500"

# Extract macs to array
MACS_LIST=$(ip link show |\
grep -o -E -e '(([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2}))' |\
sort |\
uniq |\
tr '\n' ',')
IFS=$',' read -a MACS_ARRAY <<< "${MACS_LIST}"

# Write pcap-filter
if [ -f /vagrant/sys/standalone.tmp ]; then
    echo -n "ether host "
else
    echo -n "(ether [6:4] & 0xffffff00 = ${FLOWGEN_ID}) and ether host "
fi
for i in "${!MACS_ARRAY[@]}"; do
    mac="${MACS_ARRAY[i]}"
    if ! ${FIRST}; then
        echo -n "and "
    fi
    echo -n "not ${mac} "
    FIRST=false
done
