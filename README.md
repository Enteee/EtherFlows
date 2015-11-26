# EtherFlows
_L2 powered flow processing._

## Idea
With a mapping of RSS-generated flow hashes into MAC address-space we can achive simple flow distribution with switching hardware. The [Flow Gen][flowgen] program does the Flow -> MAC mapping, the [Flow worker][flowworker] implements a sample flow processor.

![Set up](https://raw.githubusercontent.com/Enteee/EtherFlows/develop/doc/setup.png)

## Getting started
1. Clone this repository

    ```sh
    $ git clone --recursive https://github.com/Enteee/EtherFlows.git
    ```

2. Download & install [docker-compose][docker-compose]
  * [arch linux](https://www.archlinux.org/)

    ```sh
    $ pacman --noconfirm -S docker-compose python-pytz
    ```

  * apt-based, e.g: debian, ubuntu, ...

    ```sh
    $ apt-get install -y docker-compose
    ```

3. Start [docker][docker]

    ```sh
    $ systemctl start docker
    ```
    
3. Navigate to the flow worker directory

    ```sh
    $ cd flowworker/
    ```
4. Start the flow worker

    ```sh
    $ ./start_up.sh -S -i [SNIFFING NIC]
    ```

5. Open [Kibana @ http://127.0.0.1:5601](http://127.0.0.1:5601)
6. Done!
7. Join [#EtherFlows @freenode.net][irc]

## Requirments
### Analysis network
* Configure the same [MAC address aging time][mac aging] on all the switches, the minimum [MAC address aging time][mac aging] will be your flow timeout.
* Only a hierarchical switching topology will work (no loops allowed)
* Disable STP / RSTP or similar protocols on all switches

### Flow Gen
* [dpdk >= 2.1.0][dpdk]

### Flow Worker
* [python3][python3]
 * [python-pytz][python-pytz]

[flowgen]:flowgen/flowgen.c
[flowworker]:flowworker/flowworker.py

[dpdk]:http://dpdk.org/
[python3]:https://www.python.org
[python-pytz]:http://pytz.sourceforge.net/
[docker-compose]:https://docs.docker.com/compose/
[docker]:https://www.docker.com/
[irc]:http://webchat.freenode.net/?nick=newEtherFlowsUser&channels=EtherFlows
[mac aging]:https://www.juniper.net/documentation/en_US/junos13.2/topics/concept/bridging-mac-aging.html
