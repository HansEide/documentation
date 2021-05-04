(fram)=

# Fram

Named after the Norwegian arctic expedition ship [Fram](http://en.wikipedia.org/wiki/Fram),
the new Linux cluster hosted at [UiT Arctic University of Norway](https://uit.no/startsida) is a shared resource for research computing capable of 1.1 PFLOP/s
theoretical peak performance.

Fram is a distributed memory system which consists of 1004 dual socket and 2
quad socket nodes, interconnected with a high-bandwidth low-latency Infiniband
network. The interconnect network is organized in an island topology, with 9216
cores in each island. Each standard compute node has two 16-core Intel Broadwell
chips (2.1 GHz) and 64 GiB memory. In addition, 8 larger memory nodes with 512
GiB RAM and 2 huge memory quad socket nodes with 6 TiB of memory is provided.
The total number of compute cores is 32256.

| Details     | Fram     |
| :------------- | :------------- |
| System     |Lenovo NeXtScale nx360  |
| Number of Cores     |	32256  |
| Number of nodes     |	1006  |
| CPU type     |	Intel E5-2683v4 2.1 GHz <br>Intel E7-4850v4 2.1 GHz (hugemem)  |
| Max Floating point performance, double     |	1.1 Petaflop/s  |
| Total memory     |	78 TiB  |
| Total disc capacity     |	2.5 PB  |
