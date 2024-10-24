# This file is part of https://github.com/hilch/canopen-message-interpreter.
#
#    canopen-message-interpreter is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    canopen-message-interpreter is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with canopen-message-interpreter.  If not, see <http://www.gnu.org/licenses/>.

from enum import Enum
import re
import csv
import locale
from modules.canobjects import *
import configparser

locale.setlocale(locale.LC_ALL, "")


class CanTraceEntry:
    HEADER = [
        "Message Number",
        "Time [ms]",
        "ID",
        "DLC",
        "Data Bytes",
        "CANopen",
        "Node",
        "Index",
        "Subindex",
        "Interpretation",
        "SDO Name",
        "SDO Value (hex)",
        "SDO Value (int)",
    ]

    """
    > number : number of message
    > milliseconds : timestamp of message in milliseconds
    > canID : CAN-ID
    > dlc : CAN data length code
    > data : can data (0 - 8 bytes)
    """

    def __init__(
        self,
        number: int,
        milliseconds: float,
        canId: int,
        dlc: int,
        data: bytes,
        eds_dict,
    ):
        self.number = number
        self.milliseconds = milliseconds
        self.canId = canId
        self.dlc = dlc
        self.data = data
        self.eds_dict = eds_dict

    @property
    def dataBytes(self) -> bytes:
        if self.data is None:
            return ""
        else:
            result = "["
            for i, d in enumerate(self.data):
                if i != 0:
                    result += " "
                result = result + format(d, "#04x")
            return result + "]"

    @property
    def canOpen(self) -> CanOpenMessage:
        return CanOpenMessage(
            self.number,
            self.milliseconds,
            self.canId,
            self.dlc,
            self.data,
            self.eds_dict,
        )


class CanTrace:
    class CanTraceType(Enum):
        UNKNOWN = (0,)
        PCANVIEW1 = 1
        PCANVIEW2 = 2

    class CSVDialect(Enum):
        EXCEL_DIALECT1 = 1  # delimiter= ';', quotechar="'"

    """
    > filename: trace file name
    """

    def __init__(self):
        self.canTraceType = CanTrace.CanTraceType.UNKNOWN
        self.entries = list()

    def toCSV(self, csvfilename, dialect=CSVDialect.EXCEL_DIALECT1):
        with open(csvfilename, "w", newline="") as f:
            if dialect == CanTrace.CSVDialect.EXCEL_DIALECT1:
                writer = csv.writer(f, delimiter=";", quotechar="'")
            writer.writerow(CanTraceEntry.HEADER)
            for e in self.entries:
                interpreted = e.canOpen
                writer.writerow(
                    [
                        e.number,
                        locale.format_string("%01.3f", e.milliseconds),
                        format(e.canId, "#06x"),
                        e.dlc,
                        e.dataBytes,
                        interpreted.canOpenObject.name,
                        interpreted.nodeNumber if interpreted.nodeNumber > 0 else "-",
                        (
                            format(interpreted.index, "#06x")
                            if interpreted.index > 0
                            else "-"
                        ),
                        interpreted.subindex if interpreted.index > 0 else "-",
                        interpreted.text,
                        getattr(interpreted, "sdo_name", "-"),
                        getattr(interpreted, "sdo_value_hex", "-"),
                        getattr(interpreted, "sdo_value", "-"),
                    ]
                )


class PCANViewTrace(CanTrace):
    patternFileVersion = re.compile(r"(\$FILEVERSION=)(\d)\.(\d)")
    patternEntryV1 = re.compile(
        r"\s*(\d+)\x29\s*(\d+\.*\d*)\s*(Rx|Tx)\s*([0-9A-F]+)\s*([0-8])\s*(.*)"
    )
    patternEntryV2 = re.compile(
        r"\s*(\d+)\s*(\d+\.*\d*)\s*([A-Z]{2})\s*(\d)\s*([0-9A-F]+)\s*(Rx|Tx)\s*-\s*([0-8])\s*\s*(.*)"
    )
    patternData = re.compile(r"([0-9A-F]{2})")

    """
    > filename: trace file name (*.trc)
    """

    def __init__(self, filename, eds_filename: str):
        super().__init__()

        # load eds if any
        eds_dict = {}
        if eds_filename is not None:
            eds_dict = configparser.ConfigParser()
            eds_dict.read(eds_filename)

        with open(filename, "r") as f:
            self.canTraceTyp = __class__.CanTraceType.UNKNOWN
            content = f.readlines()
            for r in content:
                if self.canTraceTyp == __class__.CanTraceType.UNKNOWN:
                    matches = PCANViewTrace.patternFileVersion.findall(r)
                    if matches:
                        if matches[0][1] == "1":
                            self.canTraceTyp = __class__.CanTraceType.PCANVIEW1
                        elif matches[0][1] == "2":
                            self.canTraceTyp = __class__.CanTraceType.PCANVIEW2

                if self.canTraceTyp == __class__.CanTraceType.PCANVIEW1:
                    matches = __class__.patternEntryV1.findall(r)
                    if matches:
                        m = matches[0]
                        n = int(m[0])  # message number
                        ms = float(m[1])  # milliseconds
                        rxtx = m[2]
                        id = int(m[3], 16)  # CAN id
                        dlc = int(m[4])  # DLC
                        load = m[5]  # data load
                        data = bytes()

                        if load.startswith("RTR"):
                            data = None
                        else:
                            data = PCANViewTrace.patternData.findall(load)
                            data = bytes(int(d, 16) for d in data)

                        self.entries.append(
                            CanTraceEntry(
                                number=n,
                                milliseconds=ms,
                                canId=id,
                                dlc=dlc,
                                data=data,
                                eds_dict=eds_dict,
                            )
                        )

                elif self.canTraceTyp == __class__.CanTraceType.PCANVIEW2:
                    matches = __class__.patternEntryV2.findall(r)
                    if matches:
                        m = matches[0]
                        n = int(m[0])  # message number
                        ms = float(m[1])  # milliseconds
                        typ = m[2]  ## DT or RR
                        bus = int(m[3])  # bus number
                        id = int(m[4], 16)  # CAN id
                        rxtx = m[5]
                        dlc = int(m[6])  # DLC
                        load = m[7]
                        data = bytes()
                        if typ == "RR":  # RTR
                            data = None
                        else:
                            data = PCANViewTrace.patternData.findall(load)
                            data = bytes(int(d, 16) for d in data)

                        self.entries.append(
                            CanTraceEntry(
                                number=n,
                                milliseconds=ms,
                                canId=id,
                                dlc=dlc,
                                data=data,
                                eds_dict=eds_dict,
                            )
                        )
