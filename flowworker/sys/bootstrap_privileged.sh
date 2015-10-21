#!/usr/bin/env bash

cp  /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
cat << 'EOF' > /etc/pacman.d/mirrorlist
## Germany
Server = http://mirror.23media.de/archlinux/$repo/os/$arch
Server = http://archlinux.limun.org/$repo/os/$arch
Server = https://archlinux.limun.org/$repo/os/$arch
Server = http://artfiles.org/archlinux.org/$repo/os/$arch
Server = http://mirror5.bastelfreak.org/archlinux/$repo/os/$arch
Server = http://mirror.euserv.net/linux/archlinux/$repo/os/$arch
Server = http://ftp.fau.de/archlinux/$repo/os/$arch
Server = https://ftp.fau.de/archlinux/$repo/os/$arch
Server = http://mirror.flipez.de/archlinux/$repo/os/$arch
Server = http://mirror.fluxent.de/archlinux/$repo/os/$arch
Server = https://mirror.fluxent.de/archlinux/$repo/os/$arch
EOF

# Update system
pacman --noconfirm -Syu
pacman --needed --noconfirm -S  jdk8-openjdk \
                                screen  \
                                rxvt-unicode-terminfo \
                                wireshark-cli \
                                libpcap \
                                tcpdump \
                                scapy \
                                wget \
                                ruby \
                                python2-configargparse \
                                ntp \
                                htop \
                                vim
# Ruby bundler
gem install bundler

# Wireshark non root config
gpasswd -a vagrant wireshark

# Start ntp service 
systemctl start ntpd

# Disable ipv6 on sniffing interface
sysctl -w net.ipv6.conf.enp0s9.disable_ipv6=1
cat << EOF > /etc/sysctl.d/disable_ipv6.conf
net.ipv6.conf.enp0s9.disable_ipv6 = 1
EOF
