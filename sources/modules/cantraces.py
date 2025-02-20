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
from pathlib import Path
import re
import csv
import locale
from modules.canobjects import *

locale.setlocale(locale.LC_ALL, '')


class CanTraceType(Enum):
    UNKNOWN = 0,
    PCANVIEW_1_1 = 1 # tested PCAN-View Fileversion 1.1
    PCANVIEW_2_1 = 2 # tested PCAN-View Fileversion 2.1
    IXXAT_MINIMON_3 = 3 # tested IXXAT MiniMon V3

class CSVDialect(Enum):
    EXCEL_DIALECT1 = 1 # delimiter= ';', quotechar="'"


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
        if self.data is None:
            return ''
        else:
            result = '['
            for i, d in enumerate(self.data):
                if i != 0 : result += ' '
                result = result + format(d, '#04x')
            return result + ']'
    
    @property
    def canOpen(self) -> CanOpenMessage:
        return CanOpenMessage( self.number, self.milliseconds, self.canId, self.dlc, self.data )


class CanTrace():
    '''
    > filename: trace file name
    '''
    def __init__(self ):
        self.canTraceType = CanTraceType.UNKNOWN
        self.entries = list()


    def toCSV(self, csvfilename, dialect = CSVDialect.EXCEL_DIALECT1 ):
        with open( csvfilename, 'w', newline= '') as f:
            if dialect == CSVDialect.EXCEL_DIALECT1:
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
                                interpreted.nodeNumber if interpreted.nodeNumber > 0 else '-',
                                format( interpreted.index, '#06x' ) if interpreted.index > 0 else '-',
                                interpreted.subindex if interpreted.index > 0 else '-',
                                interpreted.text  ] )



class PCANViewTrace_1_1( CanTrace):
    patternEntry = re.compile(r'\s*(\d+)\x29\s*(\d+\.*\d*)\s*(Rx|Tx)\s*([0-9A-F]+)\s*([0-8])\s*(.*)')
    patternData = re.compile(r'([0-9A-F]{2})')

    '''
    > filename: trace file name (*.trc)
    '''
    def __init__(self, filename ): 
        super().__init__()
        with open(filename, 'r') as f:
            content = f.readlines()
            for r in content:
                matches = __class__.patternEntry.findall(r)
                if matches:
                    m = matches[0]
                    n = int(m[0]) # message number
                    ms = float(m[1]) # milliseconds
                    rxtx = m[2]
                    id = int(m[3],16) # CAN id
                    dlc = int(m[4]) # DLC
                    load : str = m[5] # data load                        
                    data = bytes()

                    if load.startswith('RTR') :
                        data = None
                    else:
                        data = __class__.patternData.findall(load)
                        data = bytes(int(d,16) for d in data)

                    self.entries.append( CanTraceEntry( number = n, milliseconds = ms, canId = id, dlc = dlc, data = data ) )



class PCANViewTrace_2_1( CanTrace):
    patternEntry = re.compile(r'\s*(\d+)\s*(\d+\.*\d*)\s*([A-Z]{2})\s*(\d)\s*([0-9A-F]+)\s*(Rx|Tx)\s*-\s*([0-8])\s*\s*(.*)')
    patternData = re.compile(r'([0-9A-F]{2})')

    '''
    > filename: trace file name (*.trc)
    '''
    def __init__(self, filename ): 
        super().__init__()
        with open(filename, 'r') as f:
            content = f.readlines()
            for r in content:
                matches = __class__.patternEntry.findall(r)
                if matches:
                    m = matches[0]
                    n = int(m[0]) # message number
                    ms = float(m[1]) # milliseconds
                    typ = m[2] ## DT or RR
                    bus = int(m[3]) # bus number
                    id = int(m[4],16) # CAN id
                    rxtx = m[5]
                    dlc = int(m[6]) # DLC
                    load = m[7]                         
                    data = bytes()
                    if typ == 'RR' : # RTR
                        data = None
                    else:
                        data = __class__.patternData.findall(load)
                        data = bytes(int(d,16) for d in data)

                    self.entries.append( CanTraceEntry( number = n, milliseconds = ms, canId = id, dlc = dlc, data = data ) )           



class IXXATTrace( CanTrace):
    patternEntry = re.compile(r'"(\d{2}):(\d{2}):(\d{2}\.\d*)";"(\d{1,3})";"(\w*)";"([\w\s]*)";"([\w\s=]*)"')
    patternData = re.compile(r'([0-9A-F]{2})')
    patternRTR = re.compile(r'Remote request\s*DLC\s*=\s*(\d)')

    '''
    > filename: trace file name (*.CSV)
    '''
    def __init__(self, filename ): 
        super().__init__()
        n = 0 # message number
        with open(filename, 'r') as f:
            content = f.readlines()
            for r in content:
                matches = __class__.patternEntry.findall(r)
                if matches:
                    n = n + 1
                    m = matches[0]
                    hour = int(m[0])
                    minute = int(m[1])
                    seconds = float(m[2])
                    ms = (hour * 3600 + minute * 60 + seconds) * 1000
                    id = int(m[3],16)
                    format = m[4] # 'Std' or 'Ext' ?`
                    flags = m[5] # 'Rtr' or ?
                    load = m[6] # data load or RTR information
                    data = bytes
                    dlc = 0

                    if 'Rtr' in flags:
                        data = None
                        dlc = int( __class__.patternRTR.findall(load)[0] )
                    else:
                        data = __class__.patternData.findall(load)
                        data = bytes(int(d,16) for d in data)
                        dlc = len(data)

                    if n == 571:
                        pass
                    self.entries.append( CanTraceEntry( number = n, milliseconds = ms, canId = id, dlc = dlc, data = data ) )



def OpenTraceFile( filename : str ) -> CanTrace:

    headers = {
        re.compile(r";\$FILEVERSION=1\.1[\s\S]*\$STARTTIME[\s\S]*Generated by"): CanTraceType.PCANVIEW_1_1,
        re.compile(r";\$FILEVERSION=2\.1[\s\S]*\$STARTTIME[\s\S]*\$COLUMNS[\s\S]*Generated by") : CanTraceType.PCANVIEW_2_1,
        re.compile(r"ASCII Trace IXXAT MiniMon V3\s*Version:") : CanTraceType.IXXAT_MINIMON_3
    }    

    file = Path(filename)
    if file.is_file():
        with open(filename, 'r') as f:
            h = []
            for i in range(0, 16):
                h.append(f.readline())
            fileHeader = ''.join(h)

            for k, v in headers.items():
                m = k.match(fileHeader)
                if m:
                    if v == CanTraceType.PCANVIEW_1_1:
                        print( f'convert {filename} from PCAN-View 1.1' )
                        return PCANViewTrace_1_1( filename )
                    elif v == CanTraceType.PCANVIEW_2_1:
                        print( f'convert {filename} from PCAN-View 2.1' )
                        return PCANViewTrace_2_1( filename )
                    elif v == CanTraceType.IXXAT_MINIMON_3:
                        print( f'convert {filename} from IXXAT MiniMon V3' )
                        return IXXATTrace( filename )
                
            print( 'unknown trace file format' )
            return None
    else:
        print( 'file not found' )
        return None
    


        
