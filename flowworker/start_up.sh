#!/usr/bin/env bash

INTERFACE_GIVEN=false
IGNORED_INTERFACES="lo"
INSTANCE_DIR="./instances"
WORKDIR="$(pwd)"
STOP=false
AUTOMATIC=false

function usage {
    cat << EOF
    usage: ${0} [OPTIONS]
    OPTIONS:
        -i interface    :   Interface to provision VM for
        -d instance dir :   Instance directory
        -a              :   Automatic provisioning
        -h              :   Print this help
        -s              :   Stops all the VMs
EOF
}

function enter {
    if ! ${AUTOMATIC}; then
        echo "[ENTER]"
        read
    fi
}

#Options options
while getopts "i:d:ash" opt; do
    case $opt in
    i)
        INTERFACES="${INTERFACES} ${OPTARG}"
        INTERFACE_GIVEN=true
    ;;
    d)
        INSTANCE_DIR="${OPTARG}"
    ;;
    a)
        AUTOMATIC=true
    ;;
    s)
        STOP=true
    ;;
    h)
        usage
        exit 0;
    ;;
    \?)
        echo "Invalid option: -${OPTARG}"
        usage
        exit 1;
    ;;
  esac
done
shift $(expr $OPTIND - 1 )

if ! ${INTERFACE_GIVEN} ; then
    INTERFACES=$(ip link show | \
        sed -nre 's/^[0-9]+: (.+?): .*/\1/p' | \
        grep -v "${IGNORED_INTERFACES}")
fi
echo "Interfaces:"
echo "${INTERFACES}"
enter

for i in ${INTERFACES}; do
    (
        instance="${INSTANCE_DIR}/${i}"
        mkdir -p "${instance}"
        ( cd "${instance}" && vagrant halt)
        rm -rf "${instance}"
        if ! ${STOP}; then
            # create directory structure
            find . -path "${INSTANCE_DIR}" -prune -o -type d -exec mkdir -p "${instance}/{}" \;
            find . -path "${INSTANCE_DIR}" -prune -o -type f -exec cp {} "${instance}/{}" \;
            cd "${instance}"
            sed -i -- "s/auto_config: false/auto_config: false, bridge: \"${i}\"/g" Vagrantfile
            vagrant destroy <<< "y\n"
            vagrant up
        fi
    ) &
done
wait
