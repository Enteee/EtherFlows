#!/usr/bin/env bash
WORK_DIR="$(pwd)"
FLOWGEN_ID="0xBADA5500"
AUTOMATIC=false
STANDALONE=false
SNIFFING_INTERFACE=""
GOSSIP_IP="127.0.0.1"
ES_HEAP_SIZE="4g"

UNAME=$(uname -s)
ELK_STACK=true

function usage {
    cat << EOF
    usage: ${0} -i interface [OPTIONS]
    OPTIONS:
        -i interface    :   Sniffing interface
        -g gossip ip    :   IP of an ES instance which acts as a gossip router for the cluster
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
        echo "port not 9200 and port not 9300 and port not 5000 and port not 5601"
    else
        # Flowgen: only accept traffic from flowgen
        echo "(ether [6:4] & 0xffffff00 = ${FLOWGEN_ID})"
    fi
}

#Options options
while getopts "i:g:H:asSh" opt; do
    case $opt in
    i)
        SNIFFING_INTERFACE="${OPTARG}"
    ;;
    g)
        GOSSIP_IP="${OPTARG}"
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

if ! ip link show "${SNIFFING_INTERFACE}" &>/dev/null; then
    echo "Invalid sniffing interface: ${SNIFFING_INTERFACE}"
    usage
    exit 1
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
    export ES_ZEN_UNICAST_HOST="${GOSSIP_IP}" && \
    export ES_HEAP_SIZE="${ES_HEAP_SIZE}"  && \
    sudo -E docker-compose up 
    ) &
fi

# wait until logstash is accepting input
until nc -z localhost 5000; do echo "Waiting for logstash..."; sleep 1;done

sudo sh -c "
    tshark -i '${SNIFFING_INTERFACE}' -q -lT pdml '$(pcap_filter)' | \
    ${WORK_DIR}/flowworker.py -i '${SNIFFING_INTERFACE}' | \
    nc localhost 5000
"

if ${ELK_STACK}; then
    sudo docker-compose stop
fi
