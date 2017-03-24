# Copyright (C) 2014
#
# Douglas Schilling Landgraf
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

import datetime
import fcntl
import getpass
import os
import sys
import time
import tty
import termios

from netstat import NetStat


class FormatDisplay:
    LISTEN, HUMAN_BEING, HEX = range(0, 3)


class Color:
    BLUE, RED = range(0, 2)


class Filter:
    IP, PORT, IP_PORT, STATE, USER = range(0, 5)


class Highlight:
    IP, PORT, IP_PORT, STATE, USER = range(0, 5)


def _print_colored(color, raw_str):
    ASCII_WHITE_TEXT_BACKGROUND_RED = "\x1b[41m"
    ASCII_WHITE_TEXT_BACKGROUND_BLUE = "\x1b[44m"
    ASCII_WHITE_TEXT_BACKGROUND_BLACK = "\x1b[49m\r"

    if color == Color.RED:
        print("%s" %
              ASCII_WHITE_TEXT_BACKGROUND_RED +
              raw_str +
              ASCII_WHITE_TEXT_BACKGROUND_BLACK
              )

    if color == Color.BLUE:
        print("%s" %
              ASCII_WHITE_TEXT_BACKGROUND_BLUE +
              raw_str +
              ASCII_WHITE_TEXT_BACKGROUND_BLACK
              )


class Terminal:
    def __init__(self):
        # Get current terminal settings
        self.previous_terminal_mode = termios.tcgetattr(sys.stdin.fileno())


    def set_default(self):
        termios.tcsetattr(
            sys.stdin.fileno(),
            termios.TCSADRAIN,
            self.previous_terminal_mode
        )

    def set_raw(self):
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NDELAY)
        tty.setraw(sys.stdin.fileno())


class NetPath:
    def __init__(self):
        # Default format at start
        self.output_format = FormatDisplay.LISTEN

        self.filter = None
        self.filter_data = None
        self.filter_type = None

        self.highlight = None
        self.highlight_data = None
        self.highlight_type = None

        self.terminal = Terminal()

    def help(self):
        self.terminal.set_default()

        print("c - clear any created highlight or filter")
        print("f - filter the screen by ip address, port, state or user")
        print("h - print this screen")
        print("H - highlight a ip address, port, state or user")
        print("l - logging filtered or highlight hosts")
        print("n - next (mode) system status screen")
        print("q - quit")

        # stdin already consumed to get the option from while
        # reopening stdin
        sys.stdin = open('/dev/tty')
        _print_colored(Color.BLUE, "press enter to exit help menu".center(60))
        raw_input("")
        self.terminal.set_raw()

    def header(self):
        if self.output_format != FormatDisplay.HEX:
            header = "{0} {1} {2} {3} {4} {5} {6}\r".format(
                "Proto",
                "Recv-Q",
                "Send-Q".rjust(6),
                "Local Address".ljust(27),
                "Foreign Address".ljust(27),
                "State".ljust(12),
                "User"
            )
        else:
            header = "{0} {1} {2} {3} {4} {5} {6}\r".format(
                "Proto",
                "Recv-Q",
                "Send-Q".rjust(8),
                "Local Address".ljust(27),
                "Foreign Address".ljust(27),
                "State".ljust(12),
                "User"
            )

        _print_colored(Color.BLUE, header)

    def footer(self):
        if self.output_format == FormatDisplay.LISTEN:
            mode = " | Mode: Listen"

        if self.output_format == FormatDisplay.HUMAN_BEING:
            mode = " | Mode: All Connections"

        if self.output_format == FormatDisplay.HEX:
            mode = " | Mode: All Connections (Hex)"

        footer = "Logged as " + getpass.getuser() + \
            " | Press h for help | " + \
            datetime.datetime.now().strftime(
                '%Y/%m/%d %H:%M'
            ) + mode

        return footer

    @property
    def output_format(self):
        return self.output_format

    @output_format.setter
    def output_format(self, value):
        self.output_format = value

    def print_highlight(self, hlight_data, hlight_type, message, data):
        if hlight_type == "ip":
            if hlight_data == data['rem_address'].split(":")[0] or \
                    hlight_data == data['local_address'].split(":")[0]:
                _print_colored(Color.RED, message)

        if hlight_type == "port":
            if hlight_data == data['rem_address'].split(":")[1] or \
                    hlight_data == data['local_address'].split(":")[1]:
                _print_colored(Color.RED, message)

        if hlight_type == "ip:port":
            if hlight_data == data['rem_address'] or \
                    hlight_data == data['local_address']:
                _print_colored(Color.RED, message)

        if hlight_type == "state" and hlight_data == data['st']:
            _print_colored(Color.RED, message)

        if hlight_type == "user" and hlight_data == data['uid']:
            _print_colored(Color.RED, message)

    def print_filter(self, filter_data, filter_type, message, data):
        if filter_type == "ip":
            if filter_data == data['rem_address'].split(":")[0] or \
                    filter_data == data['local_address'].split(":")[0]:
                print(message)

        if filter_type == "port":
            if filter_data == data['rem_address'].split(":")[1] or \
                    filter_data == data['local_address'].split(":")[1]:
                print(message)

        if filter_type == "ip:port":
            if filter_data == data['rem_address'] or \
                    filter_data == data['local_address']:
                print(message)

        if filter_type == "state" and filter_data == data['st']:
            print(message)

        if filter_type == "user" and filter_data == data['uid']:
            print(message)

    def set_display_filter(self):
        fmt = "human_being"
        self.filter = Filter.STATE
        self.filter_type = "state"
        self.filter_data = "LISTEN"

        if self.output_format == FormatDisplay.HUMAN_BEING:
            fmt = "human_being"
            self.filter = None
            self.filter_type = None
            self.filter_data = None

        if self.output_format == FormatDisplay.HEX:
            fmt = "hex"
            self.filter = None
            self.filter_type = None
            self.filter_data = None
        return fmt

    def set_filter(self, filter):
        if filter == Filter.IP:
            self.filter_type = "ip"
            self.filter_data = raw_input("Type the IP:")

        if filter == Filter.PORT:
            self.filter_type = "port"
            self.filter_data = raw_input("Type the Port:")

        if filter == Filter.IP_PORT:
            self.filter_type = "ip:port"
            self.filter_data = raw_input("Type the IP:Port:")

        if filter == Filter.STATE:
            self.filter_type = "state"
            self.filter_data = raw_input("Type State:")

        if filter == Filter.USER:
            self.filter_type = "user"
            self.filter_data = raw_input("Type User:")

    def cleandata(self):
        self.highlight = None
        self.highlight_data = None
        self.highlight_type = None
        self.filter = None
        self.filter_data = None
        self.filter_type = None

    def set_highlight(self, highlight):
        if highlight == Highlight.IP:
            self.highlight_type = "ip"
            self.highlight_data = raw_input("Type the IP:")

        if highlight == Highlight.PORT:
            self.highlight_type = "port"
            self.highlight_data = raw_input("Type the Port:")

        if highlight == Highlight.IP_PORT:
            self.highlight_type = "ip:port"
            self.highlight_data = raw_input("Type the IP:Port:")

        if highlight == Highlight.STATE:
            self.highlight_type = "state"
            self.highlight_data = raw_input("Type State:")

        if highlight == Highlight.USER:
            self.highlight_type = "user"
            self.highlight_data = raw_input("Type User:")

if __name__ == "__main__":

    netpath = NetPath()
    netstat = NetStat()
    terminal = Terminal()

    # Set raw because raw_input() expect 'enter' from users
    # after they press any key
    terminal.set_raw()

    while True:
        os.system('clear')

        header = netpath.header()
        format = netpath.set_display_filter()

        for data in netstat.collect_net_tcp(ret_format=format):
            rx, tx = data['tx_queue_rx_queue'].split(":")

            # Layout for non hex screen
            if netpath.output_format != FormatDisplay.HEX:
                line = "{0} {1} {2} {3} {4} {5} {6}\r".format(
                    data['proto'],
                    rx.rjust(8),
                    tx.rjust(6),
                    data['local_address'].ljust(27),
                    data['rem_address'].ljust(27),
                    data['st'].ljust(12),
                    data['uid']
                )

            # Layout for hex screen (the fields size are different)
            if netpath.output_format == FormatDisplay.HEX:
                line = "{0} {1} {2} {3} {4} {5} {6}\r".format(
                    data['proto'],
                    rx.rjust(8),
                    tx.rjust(6),
                    data['local_address'].ljust(27),
                    data['rem_address'].ljust(27),
                    data['st'].ljust(12),
                    data['uid']
                )

            if netpath.highlight is not None:
                netpath.print_highlight(
                    hlight_data=netpath.highlight_data,
                    hlight_type=netpath.highlight_type,
                    message=line,
                    data=data
                )
                continue

            if netpath.filter is not None:
                netpath.print_filter(
                    filter_data=netpath.filter_data,
                    filter_type=netpath.filter_type,
                    message=line,
                    data=data
                )
                continue

            print(line)

        footer = netpath.footer()
        _print_colored(Color.BLUE, footer.center(95))

        try:
            getch = sys.stdin.read(1)
            if getch == 'c':
                netpath.cleandata()

            if getch == 'n':
                if netpath.output_format < FormatDisplay.HEX:
                    netpath.output_format += 1
                else:
                    netpath.output_format = FormatDisplay.LISTEN

            if getch == 'h':
                netpath.help()

            if getch == 'q':
                terminal.set_default()
                sys.exit(0)

            if getch == 'f':
                terminal.set_default()
                # stdin already consumed to get the option from while
                # reopening stdin
                sys.stdin = open('/dev/tty')

                print "Filter mode, please select the field below:"
                print "[1] IP [2] Port [3] IP:PORT [4] State [5] User"

                try:
                    _FILTER = int(raw_input(">"))
                except ValueError:
                    Terminal.set_raw()
                    continue

                if _FILTER < Filter.IP or _FILTER > Filter.USER:
                    Terminal.set_raw()
                    continue

                netpath.get_filter_data(_FILTER)
                terminal.set_raw()

            if getch == 'H':
                terminal.set_default()
                # stdin already consumed to get the option from while
                # reopening stdin
                sys.stdin = open('/dev/tty')

                print "Highlight mode, please select the field below:"
                print "[1] IP [2] Port [3] IP:PORT [4] State [5] User"

                try:
                    _HIGHLIGHT = int(raw_input(">"))
                except ValueError:
                    terminal.set_raw()
                    continue

                if _HIGHLIGHT < Highlight.IP or \
                        _HIGHLIGHT > Highlight.USER:
                    terminal.set_raw()
                    continue

                netpath.set_highlight(_HIGHLIGHT)
                terminal.set_raw()
        except IOError:
            pass

        time.sleep(1)
