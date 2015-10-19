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
    $ ./start_up.sh -i [Sniffing NIC]
    ```

6. Open [http://localhost:5601](http://localhost:5601)
7. Done!
8. Join [#EtherFlows @freenode.net][irc]

## Requirments
### Flow Gen
* [dpdk >= 2.1.0][dpdk]

### Flow Worker
* [python2][python2]
* [scapy][scapy]

[flowgen]:flowgen/flowgen.c
[flowworker]:flowworker/flowworker.py

[dpdk]:http://dpdk.org/
[python2]:https://www.python.org/download/releases/2.7.3/
[scapy]:http://www.secdev.org/projects/scapy/
[vagrant]:https://www.vagrantup.com/downloads.html
[virtualbox]:https://www.virtualbox.org/
[irc]:http://webchat.freenode.net/?nick=newEtherFlowsUser&channels=EtherFlows
