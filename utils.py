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

import struct

def split_string(string, step_chars):
    """
    string -- String to be split in 'n' step chars
    step_chars -- number to step

    """
    return [string[i:i+step_chars] for i in range(0, len(string), step_chars)]

def hex_to_dec(hex_number):
    """
    Args 
    hex_number -- A hexadecimal (base 16) number

    Transform the hex_number to decimal
    """

    return int(hex_number, 16)
