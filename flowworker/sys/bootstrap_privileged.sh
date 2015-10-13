#!/usr/bin/env bash
pacman --noconfirm -Syu
pacman --noconfirm -S jdk7-openjdk screen rxvt-unicode-terminfo wireshark-cli libpcap tcpdump

# Ruby bundler
gem install bundler

#Wireshark non root config
gpasswd -a vagrant wireshark
newgrp wireshark
