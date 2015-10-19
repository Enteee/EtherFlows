#!/usr/bin/env bash

INTERFACE_GIVEN=false
IGNORED_INTERFACES="lo"
INSTANCE_DIR="./instances"
WORKDIR="$(pwd)"
AUTOMATIC=false

function usage {
    cat << EOF
    usage: ${0} [OPTIONS]
    OPTIONS:
        -i :    List of interface to provision VM for
        -a :    Automatic provisioning
        -d :    Set instance directory
        -h :    Print this help
EOF
}

function enter {
    if ! ${AUTOMATIC}; then
        echo "[ENTER]"
        read
    fi
}

#Options options
while getopts "i:d:h" opt; do
    case $opt in
    a)
        AUTOMATIC=true
    ;;
    i)
        INTERFACES="${INTERFACES} ${OPTARG}"
        INTERFACE_GIVEN=true
    ;;
    d)
        INSTANCE_DIR="${OPTARG}"
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
        sed -nre 's/[0-9]+: (.+?): .*/\1/p' | \
        grep -v "${IGNORED_INTERFACES}")
fi
echo "Interfaces:"
echo "${INTERFACES}"
enter

echo "Removing ${INSTANCE_DIR}"
enter
rm -rf "${INSTANCE_DIR}"
mkdir -p "${INSTANCE_DIR}"

for i in ${INTERFACES}; do
    (
    if [ "${i}" == "lo" ]; then
        continue
    fi
    instance="${INSTANCE_DIR}/${i}"
    # create directory structure
    find . -path "${INSTANCE_DIR}" -prune -o -type d -exec mkdir -p "${instance}/{}" \;
    find . -path "${INSTANCE_DIR}" -prune -o -type f -exec cp {} "${instance}/{}" \;
    cd "${instance}"
    sed -i -- "s/auto_config: false/auto_config: false, bridge: \"${i}\"/g" Vagrantfile
    vagrant destroy <<< "y\n"
    vagrant up
    cd "${WORKDIR}"
    ) &
done
wait 
