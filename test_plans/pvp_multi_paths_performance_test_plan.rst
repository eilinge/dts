.. Copyright (c) <2019>, Intel Corporation
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:

   - Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.

   - Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.

   - Neither the name of Intel Corporation nor the names of its
     contributors may be used to endorse or promote products derived
     from this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
   FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
   COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
   OF THE POSSIBILITY OF SUCH DAMAGE.

=====================================
PVP multi-paths performance Tests
=====================================

Description
===========

Benchmark PVP multi-paths performance with 7 TX/RX PATHs.
Includes Mergeable, Normal, Vector_RX, Inorder mergeable, Inorder 
no-mergeable, Virtio 1.1 mergeable, Virtio 1.1 no-mergeable Path.
Give 1 core for vhost and virtio respectively.

Test Case 1: pvp test with Virtio 1.1 mergeable path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-3  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,packed_vq=1,mrg_rxbuf=1 \
    -- -i --tx-offloads=0x0 --enable-hw-vlan-strip --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.

Test Case 2: pvp test with Virtio 1.1 no-mergeable path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-3  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,packed_vq=1,mrg_rxbuf=0 \
    -- -i --tx-offloads=0x0 --enable-hw-vlan-strip --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.

Test Case 3: pvp test with Inorder mergeable path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-3  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,in_order=1 \
    -- -i --tx-offloads=0x0 --enable-hw-vlan-strip --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.

Test Case 4: pvp test with Inorder no-mergeable path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-4  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,in_order=1,mrg_rxbuf=0 \
    -- -i --tx-offloads=0x0 --enable-hw-vlan-strip --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.

Test Case 5: pvp test with Mergeable path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-4  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,in_order=0,mrg_rxbuf=1 \
    -- -i --tx-offloads=0x0 --enable-hw-vlan-strip --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.

Test Case 6: pvp test with Normal path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-4  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,in_order=0,mrg_rxbuf=0 \
    -- -i --tx-offloads=0x0 --enable-hw-vlan-strip --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.

Test Case 7: pvp test with Vector_RX path
=======================================================================

flow: 
TG --> NIC --> Vhost --> Virtio--> Vhost --> NIC --> TG

1. Bind one port to igb_uio, then launch vhost by below command::

    rm -rf vhost-net*
    ./testpmd -n 4 -l 2-4  --socket-mem 1024,1024 --legacy-mem \
    --file-prefix=vhost --vdev 'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024
    testpmd>set fwd mac
    testpmd>start

2. Launch virtio-user by below command::

    ./testpmd -n 4 -l 5-6 --socket-mem 1024,1024 \
    --legacy-mem --no-pci --file-prefix=virtio \
    --vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,in_order=0,mrg_rxbuf=0 \
    -- -i --tx-offloads=0x0 --rss-ip --nb-cores=1 --txd=1024 --rxd=1024
    >set fwd mac
    >start

3. Send packet with packet generator with different packet size, check the throughput.