# BSD LICENSE
#
# Copyright(c) 2010-2019 Intel Corporation. All rights reserved.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of Intel Corporation nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
DPDK Test suite.
Test PVP performance using virtio_user on 8 tx/rx path.
"""

import utils
from test_case import TestCase
from settings import HEADER_SIZE


class TestPVPMultiPathPerformance(TestCase):

    def set_up_all(self):
        """
        Run at the start of each test suite.
        """
        self.frame_sizes = [64, 128, 256, 512, 1024, 1518]
        self.core_config = "1S/4C/1T"
        self.number_of_ports = 1
        self.headers_size = HEADER_SIZE['eth'] + HEADER_SIZE['ip'] + \
            HEADER_SIZE['udp']
        self.dut_ports = self.dut.get_ports()
        self.verify(len(self.dut_ports) >= 1, "Insufficient ports for testing")
        self.ports_socket = self.dut.get_numa_id(self.dut_ports[0])
        self.core_list = self.dut.get_core_list(
            self.core_config, socket=self.ports_socket)
        self.core_list_user = self.core_list[0:2]
        self.core_list_host = self.core_list[2:4]
        self.core_mask_user = utils.create_mask(self.core_list_user)
        self.core_mask_host = utils.create_mask(self.core_list_host)
        if self.dut.cores[len(self.dut.cores) - 1]['socket'] == '0':
            self.socket_mem = '1024'
        else:
            self.socket_mem = '1024,1024'

    def set_up(self):
        """
        Run before each test case.
        """
        self.vhost_user = self.dut.new_session(suite="user")
        self.vhost = self.dut.new_session(suite="vhost")
        # Prepare the result table
        self.table_header = ['Frame']
        self.table_header.append("Mode")
        self.table_header.append("Mpps")
        self.table_header.append("% linerate")
        self.result_table_create(self.table_header)

    def send_and_verify(self, case_info, frame_size):
        """
        Send packet with packet generator and verify
        """
        payload_size = frame_size - self.headers_size
        tgen_input = []
        for port in xrange(self.number_of_ports):
            rx_port = self.tester.get_local_port(
                self.dut_ports[port % self.number_of_ports])
            tx_port = self.tester.get_local_port(
                self.dut_ports[(port) % self.number_of_ports])
            destination_mac = self.dut.get_mac_address(
                self.dut_ports[(port) % self.number_of_ports])
            self.tester.scapy_append(
                'wrpcap("l2fwd_%d.pcap", [Ether(dst="%s")/IP()/UDP()/("X"*%d)])' %
                (port, destination_mac, payload_size))

            tgen_input.append((tx_port, rx_port, "l2fwd_%d.pcap" % port))

        self.tester.scapy_execute()
        _, pps = self.tester.traffic_generator_throughput(tgen_input)
        Mpps = pps / 1000000.0
        self.verify(Mpps > 0, "%s can not receive packets of frame size %d" % (self.running_case, frame_size))

        throughput = Mpps * 100 / \
                     float(self.wirespeed(self.nic, frame_size, self.number_of_ports))

        results_row = [frame_size]
        results_row.append(case_info)
        results_row.append(Mpps)
        results_row.append(throughput)
        self.result_table_add(results_row)

    def start_vhost_testpmd(self):
        """
        start testpmd on vhost
        """
        self.dut.send_expect("rm -rf ./vhost.out", "#")
        self.dut.send_expect("rm -rf ./vhost-net*", "#")
        self.dut.send_expect("killall -s INT testpmd", "#")
        self.dut.send_expect("killall -s INT qemu-system-x86_64", "#")
        command_line_client = "./%s/app/testpmd -n %d -c %s --socket-mem " + \
                              " %s --legacy-mem --file-prefix=vhost --vdev " + \
                              "'net_vhost0,iface=vhost-net,queues=1,client=0' -- -i --nb-cores=1 --txd=1024 --rxd=1024"
        command_line_client = command_line_client % (self.target,
            self.dut.get_memory_channels(), self.core_mask_host, self.socket_mem)
        self.vhost.send_expect(command_line_client, "testpmd> ", 120)
        self.vhost.send_expect("set fwd mac", "testpmd> ", 120)
        self.vhost.send_expect("start", "testpmd> ", 120)

    def start_virtio_testpmd(self, args):
        """
        start testpmd on virtio
        """
        command_line_user = "./%s/app/testpmd -n %d -c %s " + \
                            " --socket-mem %s --legacy-mem --no-pci --file-prefix=virtio " + \
                            "--vdev=net_virtio_user0,mac=00:01:02:03:04:05,path=./vhost-net,%s " + \
                            "-- -i %s --rss-ip --nb-cores=1 --txd=1024 --rxd=1024"
        command_line_user = command_line_user % (self.target,
            self.dut.get_memory_channels(), self.core_mask_user,
            self.socket_mem, args["version"], args["path"])
        self.vhost_user = self.dut.new_session(suite="user")
        self.vhost_user.send_expect(command_line_user, "testpmd> ", 120)
        self.vhost_user.send_expect("set fwd mac", "testpmd> ", 120)
        self.vhost_user.send_expect("start", "testpmd> ", 120)

    def close_all_testpmd(self):
        """
        close all testpmd of vhost and virtio
        """
        self.vhost.send_expect("quit", "#", 60)
        self.vhost_user.send_expect("quit", "#", 60)

    def close_all_session(self):
        """
        close all session of vhost an virtio
        """
        self.dut.close_session(self.vhost_user)
        self.dut.close_session(self.vhost)

    def test_perf_pvp_virtio11_mergeable(self):
        """
        performance for PVP virtio 1.1 Mergeable Path.
        """
        virtio_pmd_arg = {"version": "in_order=0,packed_vq=1,mrg_rxbuf=1",
                            "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("virtio_1.1_mergeable on", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_virtio11_normal(self):
        """
        performance for PVP virtio1.1 Normal Path.
        """
        virtio_pmd_arg = {"version": "in_order=0,packed_vq=1,mrg_rxbuf=0",
                            "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("virtio_1.1_normal", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_virtio11_inorder(self):
        """
        performance for PVP virtio 1.1 inorder Path.
        """
        virtio_pmd_arg = {"version": "in_order=1,packed_vq=1,mrg_rxbuf=0",
                            "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("virtio_1.1 inorder", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_inorder_mergeable(self):
        """
        performance for PVP In_order mergeable Path.
        """
        virtio_pmd_arg = {"version": "packed_vq=0,in_order=1,mrg_rxbuf=1",
                            "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("inoder mergeable on", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_inorder_no_mergeable(self):
        """
        performance for PVP In_order no_mergeable Path.
        """
        virtio_pmd_arg = {"version": "packed_vq=0,in_order=1,mrg_rxbuf=0",
                        "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("inoder mergeable off", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_mergeable(self):
        """
        performance for PVP Mergeable Path.
        """
        virtio_pmd_arg = {"version": "packed_vq=0,in_order=0,mrg_rxbuf=1",
                            "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("virito mergeable", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_normal(self):
        """
        performance for PVP Normal Path.
        """
        virtio_pmd_arg = {"version": "packed_vq=0,in_order=0,mrg_rxbuf=0",
                            "path": "--tx-offloads=0x0 --enable-hw-vlan-strip"}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("virito normal", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def test_perf_pvp_vector_rx(self):
        """
        performance for PVP Vector Path
        """
        virtio_pmd_arg = {"version": "packed_vq=0,in_order=0,mrg_rxbuf=0",
                            "path": "--tx-offloads=0x0 "}
        for frame_size in self.frame_sizes:
            self.start_vhost_testpmd()
            self.start_virtio_testpmd(virtio_pmd_arg)
            self.send_and_verify("virito vector rx", frame_size)
            self.close_all_testpmd()
        self.result_table_print()

    def tear_down(self):
        """
        Run after each test case.
        """
        self.dut.send_expect("killall -s INT testpmd", "#")
        self.close_all_session()

    def tear_down_all(self):
        """
        Run after each test suite.
        """
