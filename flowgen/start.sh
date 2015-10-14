#!/bin/bash
sudo truncate -s 0 /tmp/eth1_tx.pcap
sudo gdb --args ./build/flowGen -c '0xf' -n 1
# --vdev 'eth_pcap1,rx_pcap=/tmp/eth1_rx.pcap,tx_pcap=/tmp/eth1_tx.pcap' 
# --vdev 'eth_pcap0,rx_pcap=/tmp/eth0_rx.pcap,tx_pcap=/tmp/eth0_tx.pcap' \
