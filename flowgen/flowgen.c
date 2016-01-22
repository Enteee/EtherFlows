/*-
 *   BSD LICENSE
 *
 *   Copyright(c) 2010-2015 Intel Corporation. All rights reserved.
 *   All rights reserved.
 *
 *   Redistribution and use in source and binary forms, with or without
 *   modification, are permitted provided that the following conditions
 *   are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in
 *       the documentation and/or other materials provided with the
 *       distribution.
 *     * Neither the name of Intel Corporation nor the names of its
 *       contributors may be used to endorse or promote products derived
 *       from this software without specific prior written permission.
 *
 *   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 *   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 *   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 *   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 *   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 *   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <unistd.h>
#include <sys/time.h>
#include <arpa/inet.h> 
#include <sys/queue.h>

#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_cycles.h>
#include <rte_lcore.h>
#include <rte_mbuf.h>
#include <rte_ether.h>
#include <rte_kvargs.h>

#define RX_RING_SIZE 128
#define TX_RING_SIZE 512

#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

/** Keepalive specification */
static const double keepalive_timeout = 2.f;
static const uint16_t keepalive_frame_len = sizeof(struct ether_hdr) + sizeof(uint32_t);
static const uint16_t keepalive_type = 0x9000;
static const struct ether_addr keepalive_addr = { .addr_bytes = {0xff} };

struct keepalive_entry {
    SLIST_ENTRY(keepalive_entry) entries;   /* Singly-linked List. */
    struct ether_addr addr;                 /**< mac of worker */
    time_t ts;                              /**< timestamp of entry */
    uint32_t delay__ms;                     /**< delay of worker in milliseconds */
};

struct keepalives {
    SLIST_HEAD(keepalive_entries, keepalive_entry) list;
    struct ether_addr min_delay_worker;
    pthread_mutex_t mutex;
};

/** globals */
static uint32_t flowgen_id;

static struct keepalives keepalives = {
    .list = SLIST_HEAD_INITIALIZER(&(keepalives.list)),
    .min_delay_worker = { { 0x0 }},
#define LOCK_KEEPALIVE (pthread_mutex_lock(&keepalives.mutex));
#define UNLOCK_KEEPALIVE (pthread_mutex_unlock(&keepalives.mutex));
    .mutex = PTHREAD_MUTEX_INITIALIZER,
};

#define UNUSED(x) (void)(x)

static const char *ARG_KEYS[] = {"id"};

static const struct rte_eth_conf port_conf_default = {
    .rxmode = {
        .mq_mode = ETH_MQ_RX_RSS,
        .max_rx_pkt_len = ETHER_MAX_LEN 
    },
    .rx_adv_conf = { .rss_conf = { 
        .rss_key = NULL,
        .rss_hf = ETH_RSS_IP 
    }
    },
};

/*
 * Initializes a given port using global settings and with the RX buffers
 * coming from the mbuf_pool passed as a parameter.
 */
static inline int
port_init(uint8_t port, struct rte_mempool *mbuf_pool)
{
    struct rte_eth_conf port_conf = port_conf_default;
    const uint16_t rx_rings = 1, tx_rings = 1;
    int retval;
    uint16_t q;

    if (port >= rte_eth_dev_count())
        return -1;

    /* Configure the Ethernet device. */
    retval = rte_eth_dev_configure(port, rx_rings, tx_rings, &port_conf);
    if (retval != 0)
        return retval;

    /* Allocate and set up 1 RX queue per Ethernet port. */
    for (q = 0; q < rx_rings; q++) {
        retval = rte_eth_rx_queue_setup(port, q, RX_RING_SIZE,
                rte_eth_dev_socket_id(port), NULL, mbuf_pool);
        if (retval < 0)
            return retval;
    }

    /* Allocate and set up 1 TX queue per Ethernet port. */
    for (q = 0; q < tx_rings; q++) {
        retval = rte_eth_tx_queue_setup(port, q, TX_RING_SIZE,
                rte_eth_dev_socket_id(port), NULL);
        if (retval < 0)
            return retval;
    }

    /* Start the Ethernet port. */
    retval = rte_eth_dev_start(port);
    if (retval < 0)
        return retval;

    /* Display the port MAC address. */
    struct ether_addr addr;
    rte_eth_macaddr_get(port, &addr);
    printf("Port %u MAC: %02" PRIx8 " %02" PRIx8 " %02" PRIx8
            " %02" PRIx8 " %02" PRIx8 " %02" PRIx8 "\n",
            (unsigned)port,
            addr.addr_bytes[0], addr.addr_bytes[1],
            addr.addr_bytes[2], addr.addr_bytes[3],
            addr.addr_bytes[4], addr.addr_bytes[5]);

    /* Enable RX in promiscuous mode for the Ethernet device. */
    rte_eth_promiscuous_enable(port);

    return 0;
}

/*
 * The lcore keepalive. This thread does listen for keepalive messages
 * and updates the worker table accordingly.
 */
static __attribute__((noreturn)) int
lcore_keepalive(__attribute__((unused)) void *arg)
{
    const uint8_t nb_ports = rte_eth_dev_count();
    uint8_t port;

    /*
     * Check that the port is on the same NUMA node as the polling thread
     * for best performance.
    */
    for (port = 0; port < nb_ports; port++)
        if (rte_eth_dev_socket_id(port) > 0 &&
                rte_eth_dev_socket_id(port) !=
                (int)rte_socket_id())
            printf("WARNING, port %u is on remote NUMA node to "
                    "polling thread.\n\tPerformance will "
                    "not be optimal.\n", port);

    printf("\nCore %u listening for keepalives. [Ctrl+C to quit]\n",
            rte_lcore_id());

    /* Run until the application is quit or killed. */
    const uint8_t port0 = 1;
    for (;;) {
        /* Receive on port0 */ 
        /* Get burst of RX packets, from first port of pair. */
        struct rte_mbuf* bufs[BURST_SIZE];
        struct rte_mbuf* keepalive_bufs[BURST_SIZE];
        size_t keepalive_bufs_count = 0;
        const uint16_t nb_rx = rte_eth_rx_burst(port0, 0,
                bufs, BURST_SIZE);
        uint16_t i = 0;
        time_t ts = time(NULL);

        if (unlikely(nb_rx == 0))
            continue;

        /* Check if keepalive packet */ 
        keepalive_bufs_count = 0;
        for(i=0;i<nb_rx;++i){
            struct rte_mbuf* buf = bufs[i];
            struct ether_hdr* ether_header = rte_pktmbuf_mtod(buf, struct ether_hdr *);
            // check if this is a keepalive packet
            if(
                    buf->data_len == keepalive_frame_len
                    && ether_header->ether_type == keepalive_type
                    && is_same_ether_addr(&(ether_header->d_addr), &keepalive_addr)
            ){
                keepalive_bufs[keepalive_bufs_count] = buf;
                ++keepalive_bufs_count;
            }
        }

        for(i=0;i<keepalive_bufs_count;++i){
            struct keepalive_entry* entry = NULL;
            struct rte_mbuf* keepalive_buf = keepalive_bufs[i];
            struct ether_hdr* ether_header = rte_pktmbuf_mtod(keepalive_buf, struct ether_hdr *);
            struct ether_addr* addr = &(ether_header->s_addr);
            // get delay in BIG endian (network byte order)
            uint32_t* delay_ptr__ms = rte_pktmbuf_mtod_offset(
                                                            keepalive_buf,
                                                            uint32_t *,
                                                            sizeof(struct ether_hdr)
                                        );
            uint32_t delay__ms = ntohl(*delay_ptr__ms);
            // TODO: faster lookup
            // check if addr exists in keepalive table
            entry = SLIST_FIRST(&(keepalives.list));
            while(entry != NULL){
                if(is_same_ether_addr(
                        &(entry->addr),
                        addr
                )){
                    // entry found
                    break;
                }
                entry = SLIST_NEXT(entry, entries);
            }

            if(entry == NULL){
                // entry not found:
                entry = calloc(1,sizeof(struct keepalive_entry));
                ether_addr_copy(addr, &(entry->addr));
                SLIST_INSERT_HEAD(&(keepalives.list), entry, entries);
            }
            // update timer & delay
            entry->ts = ts;
            entry->delay__ms = delay__ms;
        }


        // TODO: use sorted list
        // remove timed out entries from keepalive table
        // and get worker with minumum delay
        struct keepalive_entry* min_delay_entry = NULL;
        memset(&(keepalives.min_delay_worker), 0x0, sizeof(struct ether_addr));
        struct keepalive_entry* entry = SLIST_FIRST(&(keepalives.list));
        while(entry != NULL){
            struct keepalive_entry* next = SLIST_NEXT(entry, entries);
            if(difftime(
                        entry->ts,
                        ts
            ) < keepalive_timeout){
                if( min_delay_entry == NULL
                    || entry->delay__ms < min_delay_entry->delay__ms){
                    min_delay_entry = entry;
                }
            }else{
                printf("Worker has timed out\n");
                SLIST_REMOVE(&(keepalives.list), entry, keepalive_entry, entries);
                free(entry);
            }
            entry = next;
        }
        // copy min delay entry
        if(min_delay_entry != NULL){
            LOCK_KEEPALIVE;
            ether_addr_copy(&(entry->addr), &(keepalives.min_delay_worker));
            UNLOCK_KEEPALIVE;
        }

        for(i=0;i<nb_rx;++i){
            /* Free any unsent packets. */
            rte_pktmbuf_free(bufs[i]);
        }

    }
}

/*
 * The lcore main. This is the main thread that does the work, reading from
 * an input port and writing to an output port.
 */
static __attribute__((noreturn)) void
lcore_forward(void)
{
    const uint8_t nb_ports = rte_eth_dev_count();
    uint8_t port;

    /*
     * Check that the port is on the same NUMA node as the polling thread
     * for best performance.
   */
    for (port = 0; port < nb_ports; port++)
        if (rte_eth_dev_socket_id(port) > 0 &&
                rte_eth_dev_socket_id(port) !=
                (int)rte_socket_id())
            printf("WARNING, port %u is on remote NUMA node to "
                    "polling thread.\n\tPerformance will "
                    "not be optimal.\n", port);

    printf("\nCore %u forwarding packets. [Ctrl+C to quit]\n",
            rte_lcore_id());

    /* Run until the application is quit or killed. */
    const uint8_t port0 = 0;
    const uint8_t port1 = 1;
    for (;;) {
        /* Receive on port0 and forward to port1 */
        /* Get burst of RX packets, from first port of pair. */
        struct rte_mbuf *bufs[BURST_SIZE];
        const uint16_t nb_rx = rte_eth_rx_burst(port0, 0,
                bufs, BURST_SIZE);
        uint16_t i = 0;

        if(unlikely(nb_rx <= 0))
            continue;

        LOCK_KEEPALIVE;

        if(unlikely(is_zero_ether_addr(&(keepalives.min_delay_worker)))){
            printf("WARNING, no workers registered yet:"
                    "will discard %"PRIu16" packets\n", nb_rx);
            UNLOCK_KEEPALIVE;
            continue;
        }

        // send all packets to first worker
        struct ether_addr dst_addr;
        ether_addr_copy(&(keepalives.min_delay_worker), &(dst_addr));

        UNLOCK_KEEPALIVE;

        for(i=0;i<nb_rx;++i){
            struct ether_hdr* ether_header = rte_pktmbuf_mtod(bufs[i], struct ether_hdr *);
            /** Set worker destination */
            ether_addr_copy(&(dst_addr), &(ether_header->d_addr));

            /** 
             * Set source adress 
             * 3 bytes: flow gen identifier
             * 3 bytes: flow gen instance
            */
            ether_header->s_addr.addr_bytes[0] = 0xBA;
            ether_header->s_addr.addr_bytes[1] = 0xDA;
            ether_header->s_addr.addr_bytes[2] = 0x55;

            ether_header->s_addr.addr_bytes[3] = (uint8_t)( (flowgen_id >> 16) & 0xff);
            ether_header->s_addr.addr_bytes[4] = (uint8_t)( (flowgen_id >> 8) & 0xff);
            ether_header->s_addr.addr_bytes[5] = (uint8_t)(flowgen_id & 0xff);
        }

        /* Send burst of TX packets, to second port of pair. */
        const uint16_t nb_tx = rte_eth_tx_burst(port1, 0,
                bufs, nb_rx);

        /* Free any unsent packets. */
        if (unlikely(nb_tx < nb_rx)) {
            uint16_t buf;
            for (buf = nb_tx; buf < nb_rx; buf++)
                rte_pktmbuf_free(bufs[buf]);
        }
    }
}

static int handle_id_arg(const char *key, const char *value, void *opaque){
    UNUSED(opaque);
    if(strncmp(key, ARG_KEYS[0], strlen(key)) == 0){
        flowgen_id = strtol(value, NULL, 0); 
    }
    return 0;
}

/*
 * The main function, which does initialization and calls the per-lcore
 * functions.
 */
int
main(int argc, char *argv[])
{
    struct rte_kvargs* kvargs;
    struct rte_mempool *mbuf_pool;
    unsigned nb_ports;
    uint8_t portid;


    /* Generate random flowgen id */
    srand(time(NULL));
    flowgen_id = (uint32_t)rand();

    /* Initialize the Environment Abstraction Layer (EAL). */
    int ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");

    argc -= ret;
    argv += ret;

    if(argc == 2){
        kvargs = rte_kvargs_parse (
                argv[1],
                ARG_KEYS
                );

        if(kvargs == NULL)
            rte_exit(EXIT_FAILURE, "Argument parsing faled\n");

        ret = rte_kvargs_process (
                kvargs,
                ARG_KEYS[0],
                handle_id_arg,
                NULL 
                );

        if(ret < 0) 
            rte_exit(EXIT_FAILURE, "Argument processing failed\n");
    } else if(argc > 2){
        rte_exit(EXIT_FAILURE, "Too many arguments\n");
    }

    printf("Flowgen id: %u\n", flowgen_id);

    /* Check that there is an even number of ports to send/receive on. */
    nb_ports = rte_eth_dev_count();
    if (nb_ports != 2)
        rte_exit(EXIT_FAILURE, "Error: only excatly two ports supported\n");

    if (rte_lcore_count() != 2)
        rte_exit(EXIT_FAILURE,
                    "Error: need at least two lcore, %d given\n",
                    rte_lcore_count()
        );

    /* Creates a new mempool in memory to hold the mbufs. */
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS * nb_ports,
            MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());

    if (mbuf_pool == NULL)
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");

    /* Initialize all ports. */
    for (portid = 0; portid < nb_ports; portid++)
        if (port_init(portid, mbuf_pool) != 0)
            rte_exit(EXIT_FAILURE, "Cannot init port %"PRIu8 "\n",
                    portid);

    if (rte_lcore_count() > 2)
        printf("\nWARNING: Too many lcores enabled. Only 2 used.\n");

    /* call lcore_keepalive on one slave lcore*/
    rte_eal_remote_launch(lcore_keepalive, NULL, 1);

    /* Call lcore_main on the master core only. */
    lcore_forward();

    return 0;
}
