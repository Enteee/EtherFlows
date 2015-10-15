# EtherFlows
_L2 powered flow processing._

## Idea
With a mapping of RSS-generated flow hashes into MAC address-space we can achive simple flow distribution with switching hardware. The [Flow Gen][flowgen] program does the Flow -> MAC mapping, the [Flow worker][flowworker] implements a sample flow processor.

## Getting started
1. Download & install [Vagrant][vagrant] and [Virtualbox][virtualbox]
2. Make sure that you have the following modules loaded:
 * vboxdrv
 * vboxnetflt
 * vboxnetadp

    ````sh
    # cat << EOF > /etc/modules-load.d/virtualbox.conf
    vboxdrv
    vboxnetflt
    vboxnetadp
    EOF
    ````

3. Navigate to the flow worker directory
4. Start the flow worker

    ````sh
    $ vagrant up
    ````

5. Open http://localhost:5601
6. Done!
7. Join #EtherFlows @[freenode.net][freenode]

## Requirments
### Flow Gen
* [dpdk >= 2.1.0][dpdk]

### Flow Woroker
* [python2][python2]
* [scapy][scapy]

[flowgen]:flowgen/flowgen.c
[flowworker]:flowworker/flowworker.py

[dpdk]:http://dpdk.org/
[python2]:https://www.python.org/download/releases/2.7.3/
[scapy]:http://www.secdev.org/projects/scapy/
[vagrant]:https://www.vagrantup.com/downloads.html
[virtualbox]:https://www.virtualbox.org/
[freenode]:https://freenode.net/
