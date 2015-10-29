# EtherFlows
_L2 powered flow processing._

## Idea
With a mapping of RSS-generated flow hashes into MAC address-space we can achive simple flow distribution with switching hardware. The [Flow Gen][flowgen] program does the Flow -> MAC mapping, the [Flow worker][flowworker] implements a sample flow processor.

![Set up](https://raw.githubusercontent.com/Enteee/EtherFlows/develop/doc/setup.png)

## Getting started
1. Clone this repository

    ```sh
    $ git clone https://github.com/Enteee/EtherFlows.git
    ```

2. Download & install [Vagrant][vagrant] and [Virtualbox][virtualbox]
3. Make sure that you have the following modules loaded:

    ```sh
    # cat << EOF > /etc/modules-load.d/virtualbox.conf
    vboxdrv
    vboxnetflt
    vboxnetadp
    EOF
    ```

4. Navigate to the flow worker directory
5. Start the flow worker

    ```sh
    $ ./start_up.sh -c [Cluster NIC]
    ```

6. Open [Kibana @ http://127.0.0.1:5601](http://127.0.0.1:5601) or [Marvel @ http://127.0.0.1:9200/_plugin/marvel/](http://127.0.0.1:9200/_plugin/marvel/kibana/index.html)
7. Done!
8. Join [#EtherFlows @freenode.net][irc]

## Requirments
### Analysis network
* Configure the same [MAC address aging time][mac aging] on all the switches, the minimum [MAC address aging time][mac aging] will be your flow timeout.
* Only a hierarchical switching topology will work (no loops allowed)
* Disable STP / RSTP or similar protocols on all switches

### Flow Gen
* [dpdk >= 2.1.0][dpdk]

### Flow Worker
* [python2][python2]

[flowgen]:flowgen/flowgen.c
[flowworker]:flowworker/flowworker.py

[dpdk]:http://dpdk.org/
[python2]:https://www.python.org/download/releases/2.7.3/
[vagrant]:https://www.vagrantup.com/downloads.html
[virtualbox]:https://www.virtualbox.org/
[irc]:http://webchat.freenode.net/?nick=newEtherFlowsUser&channels=EtherFlows
[mac aging]:https://www.juniper.net/documentation/en_US/junos13.2/topics/concept/bridging-mac-aging.html
