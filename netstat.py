# Copyright (C) 2014
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

import pwd
import socket
import struct
import utils


class NetStat:

    def __init__(self):
        # TODO: Collectar /proc/net/tcp e tcp6.
        # icmp, udp, estatisticas, interfaces de rede
        self.conn_status = {'1': 'ESTABLISHED', '2': 'SYN_SENT',
                            '3': 'SYN_RECV',    '4': 'FIN_WAIT1',
                            '5': 'FIN_WAIT2',   '6': 'TIME_WAIT',
                            '7': 'CLOSE',       '8': 'CLOSE_WAIT',
                            '9': 'LAST_ACK',     '10': 'LISTEN',
                            '11': 'CLOSING'}

    def collect_net_tcp(self, ret_format):
        """
        Method to collect all data from /proc/net/tcp

        Arguments:
        ret_format -- Return data as hexadecimal or "human being" format ;-)
                      Use as: ret_format="hex" or ret_format="human_being"

        Returns:
        Return the /proc/net/tcp fields as list of dict
        """

        # Creates a List of dictionaries
        netdata = {}
        list_netdata = []

        data = ""
        with open("/proc/net/tcp", "r") as fd:
        #with open("/proc/net/tcp6", "r") as fd:
            for i, line in enumerate(fd):
                # Jumping header output
                if i == 0:
                    continue

                index_netstat_fields = 0
                for char in line:
                    if " " in char:
                        if data == "" or data == " " or data == "\n":
                            continue

                        data = data.strip("\n")
                        netdata['proto'] = "tcp"
                        if index_netstat_fields == 0:
                            netdata['sl'] = data

                        if index_netstat_fields == 1:
                            if ret_format == "human_being":
                                ip_address, port = data.split(":")
                                # Convert from little endian to big endian
                                ip_address = socket.inet_ntoa(
                                    struct.pack(
                                        "<L",
                                        int(ip_address, 16)
                                    )
                                )
                                netdata['local_address'] = ip_address
                                netdata['local_address'] += ":" + \
                                    str(utils.hex_to_dec(port))
                            else:
                                netdata['local_address'] = data

                        if index_netstat_fields == 2:
                            if ret_format == "human_being":
                                ip_address, port = data.split(":")
                                # Convert from little endian to big endian
                                ip_address = socket.inet_ntoa(
                                    struct.pack(
                                        "<L",
                                        int(ip_address, 16)
                                    )
                                )
                                netdata['rem_address'] = ip_address
                                netdata['rem_address'] += ":" + \
                                    str(utils.hex_to_dec(port))

                                if "0.0.0.0:0" in netdata['rem_address']:
                                    netdata['rem_address'] = "0.0.0.0:*"
                            else:
                                netdata['rem_address'] = data

                        if index_netstat_fields == 3:
                            if ret_format == "human_being":
                                netdata['st'] = self.conn_status[str(
                                    utils.hex_to_dec(data)
                                )]
                            else:
                                netdata['st'] = data

                        if index_netstat_fields == 4:
                            if ret_format == "human_being":
                                tx, rx = data.split(':')
                                netdata['tx_queue_rx_queue'] = str(
                                    utils.hex_to_dec(rx)
                                )
                                netdata['tx_queue_rx_queue'] += ":" + \
                                    str(utils.hex_to_dec(tx))
                            else:
                                netdata['tx_queue_rx_queue'] = data

                        if index_netstat_fields == 5:
                            netdata['tr_tm_when'] = data

                        if index_netstat_fields == 6:
                            netdata['retrnsmt'] = data

                        if index_netstat_fields == 7:
                            if ret_format == "human_being":
                                netdata['uid'] = pwd.getpwuid(int(data))[0]
                            else:
                                netdata['uid'] = data

                        if index_netstat_fields == 8:
                            netdata['timeout'] = data

                        if index_netstat_fields == 9:
                            netdata['inode'] = data

                        if index_netstat_fields > 9:
                            netdata['inode'] += " " + data

                        data = ""
                        index_netstat_fields += 1
                        continue

                    data += char
                list_netdata.append(netdata.copy())

            return list_netdata
