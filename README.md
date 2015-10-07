# EtherFlows
_L2 powered flow processing._

## Idea
With a mapping of RSS-generated flow hashes into MAC address-space we can achive simple flow distribution with switching hardware. The [Flow Gen][flowgen] program does the Flow -> MAC mapping, the [Flow worker][flowworker] implements a sample flow processor.

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
