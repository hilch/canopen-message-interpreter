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

locale.setlocale(locale.LC_ALL, '')


class CanTraceEntry():
    HEADER = ['Message Number', 'Time [ms]', 'ID', 'DLC', 'Data Bytes', 'CANopen', 'Node', 'Index', 'Subindex', 'Interpretation']

    '''
    > number : number of message
    > milliseconds : timestamp of message in milliseconds
    > canID : CAN-ID
    > dlc : CAN data length code
    > data : can data (0 - 8 bytes)
    '''
    def __init__(self, number : int, milliseconds : float, canId : int, dlc : int, data : bytes ):
        self.number = number
        self.milliseconds = milliseconds
        self.canId = canId
        self.dlc = dlc
        self.data = data

    @property
    def dataBytes(self) -> bytes:
        result = '['
        for i, d in enumerate(self.data):
            if i != 0 : result += ' '
            result = result + format(d, '#04x')
        return result + ']'
    
    @property
    def canOpen(self) -> CanOpenMessage:
        return CanOpenMessage( self.number, self.milliseconds, self.canId, self.dlc, self.data )


class CanTrace():
    class CanTraceType(Enum):
        UNKNOWN = 0,
        PCANVIEW1_1 = 1 

    class CSVDialect(Enum):
        EXCEL_DIALECT1 = 1 # delimiter= ';', quotechar="'"

    '''
    > filename: trace file name
    '''
    def __init__(self ):
        self.canTraceType = CanTrace.CanTraceType.UNKNOWN
        self.entries = list()


    def toCSV(self, csvfilename, dialect = CSVDialect.EXCEL_DIALECT1 ):
        with open( csvfilename, 'w', newline= '') as f:
            if dialect == CanTrace.CSVDialect.EXCEL_DIALECT1:
                writer = csv.writer(f, delimiter= ';', quotechar="'" )
            writer.writerow( CanTraceEntry.HEADER )
            for e in self.entries:
                interpreted = e.canOpen
                writer.writerow( [e.number, 
                                locale.format_string('%01.3f', e.milliseconds), 
                                format( e.canId, '#06x' ),
                                e.dlc,
                                e.dataBytes,
                                interpreted.canOpenObject.name,
                                interpreted.node if interpreted.node > 0 else '-',
                                format( interpreted.index, '#06x' ) if interpreted.index > 0 else '-',
                                interpreted.subindex if interpreted.index > 0 else '-',
                                interpreted.text  ] )



class PCANViewTrace( CanTrace):
    patternFileVersion = re.compile(r'(\$FILEVERSION=1.1)')
    patternEntry = re.compile(r'\s*(\d+)\x29\s*(\d+\.*\d*)\s*(Rx|Tx)\s*([0-9A-F]+)\s*([0-8])\s*([0-9A-F\s]{0,23})')
    patternData = re.compile(r'([0-9A-F]{2})')

    '''
    > filename: trace file name (*.trc)
    '''
    def __init__(self, filename ): 
        super().__init__()
        with open(filename, 'r') as f:
            fileVersionValid = False
            content = f.readlines()
            for r in content:
                if not fileVersionValid:
                    matches = PCANViewTrace.patternFileVersion.findall(r)
                    if matches:
                        fileVersionValid = True
                matches = PCANViewTrace.patternEntry.findall(r)
                if matches:
                    m = matches[0]
                    n = int(m[0])
                    ms = float(m[1])
                    id = int(m[3],16)
                    dlc = int(m[4])
                    data = bytes()
                    if dlc > 0:
                        data = PCANViewTrace.patternData.findall(m[5])
                        data = bytes(int(d,16) for d in data)
                    self.entries.append( CanTraceEntry( number = n, milliseconds = ms, canId = id, dlc = dlc, data = data ) )
                 
            if len(self.entries) != 0 and fileVersionValid:
                self.canTraceType = CanTrace.CanTraceType.PCANVIEW1_1
