#!/usr/bin/env bash
WORK_DIR="$(pwd)"
FLOWGEN_ID="0xBADA5500"
AUTOMATIC=false
STANDALONE=false
SNIFFING_INTERFACE=""
PCAP_FILE=""

ES_GOSSIP_IP="127.0.0.1"
ES_PUBLISH_HOST="127.0.0.1"
ES_HEAP_SIZE="4g"

UNAME=$(uname -s)
ELK_STACK=true

RUNNING=true

function usage {
    cat << EOF
    usage: ${0} <INPUT> [OPTIONS]
    INPUT: 
        -i interface    :   Sniffing interface
        -r file         :   Pcap file

    OPTIONS:
        -g gossip ip    :   IP of an ES instance which acts as a gossip router for the cluster
        -p publis ip    :   IP which should be published in the ES cluster
        -H heap size    :   Elasticsearch maximum heap size
        -a              :   Automatic provisioning
        -s              :   Starts the flowworker without a ELK environment
        -S              :   Starts the script in standalone (no flowgen) mode
        -h              :   Print this help
EOF
}

function enter() {
    if ! ${AUTOMATIC}; then
        echo "[ENTER]"
        read
    fi
}

function pcap_filter() {
    # Write pcap-filter
    if ${STANDALONE}; then
        # Standalone filter ES/Logstash/Kibana traffic
        echo "(port not 9200 and port not 9300 and port not 5000 and port not 5601)"
    else
        # Flowgen: only accept traffic from flowgen
        echo "(ether [6:4] & 0xffffff00 = ${FLOWGEN_ID})"
    fi
}

function flowworker_args() {
    # Write pcap-filter
    if ${STANDALONE}; then
        # Standalone: run in standalone mode
        echo "-S"
    fi
}

trap sigint SIGINT
function sigint(){
    RUNNING=false
}

#Options options
while getopts "i:r:g:p:H:asSh" opt; do
    case $opt in
    i)
        SNIFFING_INTERFACE="${OPTARG}"
    ;;
    r)
        PCAP_FILE="${OPTARG}"
    ;;
    g)
        ES_GOSSIP_IP="${OPTARG}"
    ;;
    p)
        ES_PUBLISH_HOST="${OPTARG}"
    ;;
    H)
        ES_HEAP_SIZE="${OPTARG}"
    ;;
    w)
        WORK_DIR="${OPTARG}"
    ;;
    a)
        AUTOMATIC=true
    ;;
    s)
        ELK_STACK=false
    ;;
    S)
        STANDALONE=true
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

if [ -z "${PCAP_FILE}" ] && [ -z "${SNIFFING_INTERFACE}" ]; then 
    echo "Ether '-i' or '-r' option is required"
    usage
    exit 1
elif [ -n "${PCAP_FILE}" ] && [ -n "${SNIFFING_INTERFACE}" ]; then 
    echo ${PCAP_FILE} ${SNIFFING_INTERFACE}
    echo "'-i' abd '-r' options can only be used exclusively"
    usage
    exit 1
fi

if [ "${UNAME}" == "Darwin" ]; then 
    echo "OS X not supported!"
    exit 1
fi
if [ -n "${SNIFFING_INTERFACE}" ]; then
    if ! ip link show "${SNIFFING_INTERFACE}" &>/dev/null; then
        echo "Invalid sniffing interface: ${SNIFFING_INTERFACE}"
        usage
        exit 1
    fi
else 
    if [ ! -f ${PCAP_FILE} ]; then
        echo "Pcap file not found"
        usage
        exit 1
    fi
fi

if  [ ! -e "${WORK_DIR}/docker-compose.yml" ] && 
    [ ! -e "${WORK_DIR}/flowworker.py" ] ;then
    echo "Invalid work dir: ${WORK_DIR}"
    usage
    exit 1
fi

#to the work dir
cd "${WORK_DIR}"

# start docker if needed
if ${ELK_STACK}; then
    (
    export ES_ZEN_UNICAST_HOST="${ES_GOSSIP_IP}" && \
    export ES_PUBLISH_HOST="${ES_PUBLISH_HOST}"  && \
    export ES_HEAP_SIZE="${ES_HEAP_SIZE}"  && \
    sudo -E docker-compose up 
    ) &
fi

if [ -n "${SNIFFING_INTERFACE}" ]; then 
    while ${RUNNING}; do 
        sudo sh -c "
            tshark -i '${SNIFFING_INTERFACE}' -q -lT pdml '$(pcap_filter)' 2>/dev/null | \
            ${WORK_DIR}/flowworker.py -i '${SNIFFING_INTERFACE}' $(flowworker_args)
        "
    done 
else 
    tshark -r "${PCAP_FILE}" -q -lT pdml 2>/dev/null | \
    ${WORK_DIR}/flowworker.py -i "${PCAP_FILE}" $(flowworker_args)
fi

