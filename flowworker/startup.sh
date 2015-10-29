#!/usr/bin/env bash
CLUSTER_INTERFACE=""
CLUSTER_INTERFACE_GIVEN=false
INTERFACE_GIVEN=false
IGNORED_INTERFACES="lo"
INSTANCE_DIR="./instances"
WORK_DIR="$(pwd)"
STOP=false
AUTOMATIC=false
STANDALONE=false
STANDALONE_FILE="sys/standalone"

UNAME=$(uname -s)
PUBLIC_NETWORK_IDENTIFIER='config\.vm\.network "public_network"'

function usage {
    cat << EOF
    usage: ${0} -c interface [OPTIONS]
    OPTIONS:
        -c interface    :   Cluster interface (mandatory, not repeated)
        -i interface    :   Sniffing interfaces (repeated)
        -d instance dir :   Instance directory
        -w workdir      :   Set the workdir (must contain Vagrantfile)
        -a              :   Automatic provisioning
        -h              :   Print this help
        -s              :   Stops all the VMs
        -S              :   Start all the VMs in standalone mode
EOF
}

function enter {
    if ! ${AUTOMATIC}; then
        echo "[ENTER]"
        read
    fi
}


if [ ${UNAME} == "Darwin" ]; then 
    echo "OS X is currently not supported"
    exit 1
fi

#Options options
while getopts "c:i:d:w:asSh" opt; do
    case $opt in
    c)
        CLUSTER_INTERFACE="${OPTARG}"
        CLUSTER_INTERFACE_GIVEN=true
    ;;
    i)
        INTERFACES="${INTERFACES} ${OPTARG}"
        INTERFACE_GIVEN=true
    ;;
    d)
        INSTANCE_DIR="${OPTARG}"
    ;;
    w)
        WORK_DIR="${OPTARG}"
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
    S)
        STANDALONE=true
    ;;
    \?)
        echo "Invalid option: -${OPTARG}"
        usage
        exit 1;
    ;;
  esac
done
shift $(expr $OPTIND - 1 )

if ! ${CLUSTER_INTERFACE_GIVEN}; then
    echo "No cluster interface given"
    usage
    exit 1
fi

if [ ! -e "${WORK_DIR}/Vagrantfile" ];then
    echo "Invalid work dir: ${WORK_DIR}"
    usage
    exit 1
fi

if ! ${INTERFACE_GIVEN} ; then
    INTERFACES=$(ip link show | \
        sed -nre 's/^[0-9]+: (.+?): .*/\1/p' | \
        grep -v "${IGNORED_INTERFACES}")
fi

cat << EOF
Cluster interface:
${CLUSTER_INTERFACE}
Sniffing interfaces:
${INTERFACES}
EOF
enter

for i in ${INTERFACES}; do
    instance="${INSTANCE_DIR}/${i}"
    interface=$(tr -d " " <<< ${i})
    hostname="$(hostname -s).${interface}"

    export VAGRANT_CLUSTER_INTERFACE="${CLUSTER_INTERFACE}"
    export VAGRANT_SNIFF_INTERFACE="${interface}"
    export VAGRANT_HOSTNAME="${hostname}"

    mkdir -p "${instance}"
    ( cd "${instance}" && vagrant destroy -f)
    rm -rf "${instance}"
    if ! ${STOP}; then
        # create directory structure
        cd "${WORK_DIR}"
        find . -path "${INSTANCE_DIR}" -prune -o -type d -exec mkdir -p "${instance}/{}" \;
        find . -path "${INSTANCE_DIR}" -prune -o -type f -exec ln "${WORK_DIR}/{}" "${instance}/{}" \;
        cd "${instance}"
        if ${STANDALONE}; then
            touch "${STANDALONE_FILE}"
        fi
        vagrant up
    fi
done
