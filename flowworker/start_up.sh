#!/usr/bin/env bash

INTERFACE_GIVEN=false
IGNORED_INTERFACES="lo"
INSTANCE_DIR="./instances"
WORK_DIR="$(pwd)"
STOP=false
AUTOMATIC=false
UNAME=$(uname -s)

function usage {
    cat << EOF
    usage: ${0} [OPTIONS]
    OPTIONS:
        -i interface    :   Interface to provision VM for
        -d instance dir :   Instance directory
        -w workdir      :   Set the workdir (must contain Vagrantfile)
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
while getopts "i:d:w:ash" opt; do
    case $opt in
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
    \?)
        echo "Invalid option: -${OPTARG}"
        usage
        exit 1;
    ;;
  esac
done
shift $(expr $OPTIND - 1 )

if [ ! -e "${WORK_DIR}/Vagrantfile" ];then
    echo "Invalid work dir: ${WORK_DIR}"
    usage
    exit 1
fi

if ! ${INTERFACE_GIVEN} ; then
    if [ ${UNAME} == "Darwin" ]; then 
        INTERFACES=$(networksetup -listallhardwareports | gawk '
            BEGIN{
                i = 1; FS=": "
            }
            /^Hardware/{
                hw[i] = $2;
            } 
            /^Device/{
                dev[i] = $2; i++
            } 
            END{
                for (j = 1; j <= i; j++){ 
                    if (match(dev[j], /^[a-z]+[0-9]+/) > 0)
                        {printf"%s %s\n",dev[j],hw[j]}
                }
            }')
    else
        INTERFACES=$(ip link show | \
            sed -nre 's/^[0-9]+: (.+?): .*/\1/p' | \
            grep -v "${IGNORED_INTERFACES}")
    fi
fi
echo "Interfaces:"
echo "${INTERFACES}"
enter

# add used boxes
(
    cd ${WORK_DIR}
    for b in $(sed -nre 's/.*config\.vm\.box = "(.+?)"/\1/p' Vagrantfile); do
        vagrant box add "${b}" &>/dev/null
    done
)
if [ ${UNAME} == "Darwin" ]; then 
    IFS=$'\n'
fi
for i in ${INTERFACES}; do
    (
        instance="${INSTANCE_DIR}/${i}"
        mkdir -p "${instance}"
        ( cd "${instance}" && vagrant destroy -f)
        rm -rf "${instance}"
        if ! ${STOP}; then
            # create directory structure
            cd "${WORK_DIR}"
            find . -path "${INSTANCE_DIR}" -prune -o -type d -exec mkdir -p "${instance}/{}" \;
            find . -path "${INSTANCE_DIR}" -prune -o -type f -exec cp {} "${instance}/{}" \;
            cd "${instance}"
            sed -i "s/config\.vm\.network \"public_network\"/\0, bridge: \"${i}\"/g" Vagrantfile

            interface=$(tr -d " " <<< ${i})
            hostname="$(hostname).${interface}"
            echo ${hostname}
            sed -i "s/vm.hostname = \"flow_worker\"/vm.hostname = \"${hostname}\"/g" Vagrantfile

            vagrant destroy -f
            vagrant up
        fi
    ) &
done
wait
