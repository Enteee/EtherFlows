#!/usr/bin/env bash

# find fastest mirror
cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
sed -i 's/^#Server/Server/' /etc/pacman.d/mirrorlist.backup
rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist

pacman --noconfirm -Syu
pacman --noconfirm -S jdk7-openjdk screen rxvt-unicode-terminfo wireshark-cli libpcap tcpdump scapy

# Ruby bundler
gem install bundler

#Wireshark non root config
gpasswd -a vagrant wireshark
