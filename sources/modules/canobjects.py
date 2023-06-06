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


# definitions from CiA 301 V4.2.0 21 February 2011

from enum import Enum, unique
from struct import unpack_from
import datetime

# 7.3.2.3 NMT state transitions table 38, 39
@unique
class CANopenType(Enum):
    NMT = 0b0000
    EMCY = 0b0001 # EMCY and SYNC
    TIME = 0b0010
    PDO1_T = 0b0011
    PDO1_R = 0b0100
    PDO2_T = 0b0101
    PDO2_R = 0b0110
    PDO3_T = 0b0111
    PDO3_R = 0b1000
    PDO4_T = 0b1001
    PDO4_R = 0b1010
    SDO_T = 0b1011
    SDO_R = 0b1100
    ERR_CTRL = 0b1110
    NONE = 0b1111




EMCY_ERRORCODE_CLASSES = { # 7.2.7.1 Emergency object usage
    0x00 : 'Error reset or no error',
    0x10 : 'Generic error',
    0x20 : 'Current',
    0x21 : 'Current, CANopen device input side',
    0x22 : 'Current inside the CANopen device',
    0x23 : 'Current, CANopen device output side',
    0x30 : 'Voltage',
    0x31 : 'Mains voltage',
    0x32 : 'Voltage inside the CANopen device',
    0x33 : 'Output voltage',
    0x40 : 'Temperature',
    0x41 : 'Ambient temperature',
    0x42 : 'CANopen device temperature',
    0x50 : 'CANopen device hardware',
    0x60 : 'CANopen device software',
    0x61 : 'Internal software',
    0x62 : 'User software',
    0x63 : 'Data set',
    0x70 : 'Additional modules',
    0x80 : 'Monitoring',
    0x81 : 'Communication',
    0x82 : 'Protocol error',
    0x90 : 'External error',
    0xF0 : 'Additional functions',
    0xFF : 'CANopen device specific'    
}


EMCY_ERRORS = { # 7.2.7.1 Emergency object usage
    0x0000 : 'Error reset or no error',
    0x1000 : 'Generic error',
    0x2000 : 'Current - generic error',
    0x2100 : 'Current, CANopen device input side - generic',
    0x2200 : 'Current inside the CANopen device - generic',
    0x2300 : 'Current, CANopen device output side - generic',
    0x3000 : 'Voltage - generic error',
    0x3100 : 'Mains voltage - generic',
    0x3200 : 'Voltage inside the CANopen device - generic',
    0x3300 : 'Output voltage - generic',
    0x4000 : 'Temperature - generic error',
    0x4100 : 'Ambient temperature - generic',
    0x4200 : 'Device temperature - generic',
    0x5000 : 'CANopen device hardware - generic error',
    0x6000 : 'CANopen device software - generic error',
    0x6100 : 'Internal software - generic',
    0x6200 : 'User software - generic',
    0x6300 : 'Data set - generic',
    0x7000 : 'Additional modules - generic error',
    0x8000 : 'Monitoring - generic error',
    0x8100 : 'Communication - generic',
    0x8110 : 'CAN overrun (objects lost)',
    0x8120 : 'CAN in error passive mode',
    0x8130 : 'Life guard error or heartbeat error',
    0x8140 : 'recovered from bus off',
    0x8150 : 'CAN-ID collision',
    0x8200 : 'Protocol error - generic',
    0x8210 : 'PDO not processed due to length error',
    0x8220 : 'PDO lengt exceeded',
    0x8230 : 'DAM MPDO not processed, destination, object not available',
    0x8240 : 'Unexpected SYNC data length',
    0x8250 : 'RPDO timeout',
    0x9000 : 'External error - generic error',
    0xF000 : 'Additional functions - generic error',
    0xFF00 : 'Device specific - generic error'
}


SDO_ABORT_CODES = {
    0x05030000: 'Toggle bit not alternated.',
    0x05040000: 'SDO protocol timed out.',
    0x05040001: 'Client/server command specifier not valid or unknown.',
    0x05040002: 'Invalid block size (block mode only).',
    0x05040003: 'Invalid sequence number (block mode only).',
    0x05040004: 'CRC error (block mode only).',
    0x05040005: 'Out of memory.',
    0x06010000: 'Unsupported access to an object.',
    0x06010001: 'Attempt to read a write only object.',
    0x06010002: 'Attempt to write a read only object.',
    0x06020000: 'Object does not exist in the object dictionary.',
    0x06040041: 'Object cannot be mapped to the PDO.',
    0x06040042: 'The number and length of the objects to be mapped would exceed PDO length.',
    0x06040043: 'General parameter incompatibility reason.',
    0x06040047: 'General internal incompatibility in the device.',
    0x06060000: 'Access failed due to an hardware error.',
    0x06070010: 'Data type does not match, length of service',
    0x06070012: 'Data type does not match, length of service parameter too high',
    0x06070013: 'Data type does not match, length of service parameter too low',
    0x06090011: 'Sub-index does not exist.',
    0x06090030: 'Invalid value for parameter (download only).',
    0x06090031: 'Value of parameter written too high (download only).',
    0x06090032: 'Value of parameter written too low (download only).',
    0x06090036: 'Maximum value is less than minimum value.',
    0x060A0023: 'Resource not available: SDO connection',
    0x08000000: 'General error',
    0x08000020: 'Data cannot be transferred or stored to the application.',
    0x08000021: 'Data cannot be transferred or stored to the application because of local control.',
    0x08000022: 'Data cannot be transferred or stored to the application because of the present device state.',
    0x08000023: 'Object dictionary dynamic generation fails or no object dictionary is present (e.g. object dictionary is generated from file and generation fails because of an file error).',
    0x08000024: 'No data available'
}



class NmtMessage():
    '''
    data: data bytes    
    '''
    def __init__( self, data : bytes ):     
        cs, self.node = unpack_from('<BB', data)
        service = { 1: 'Start', 
                    2: 'Stop', 
                    128: 'Enter Preoperational', 
                    129: 'Reset',
                    130: 'Reset communication'
                    }.get(cs, 'unknown service')
        if self.node == 0:
            self.text = f'NMT {service} all nodes'
        else:
            self.text = f'NMT {service}'


    def __repr__(self):
        return('NmtMessage: ' + self.text )

    def __str__(self):
        return(self.text )


class TimeMessage():
    '''
    data: data bytes    
    '''
    def __init__( self, data : bytes ):      
        ms, days = unpack_from('<LH', data)  
        ms = ms &  0x3fff  
        date = datetime.datetime(1984, 1, 1) + datetime.timedelta(days = days, milliseconds=ms)
        self.text = f'TIME ms:{ms} ({date.isoformat()})'

    def __repr__(self):
        return('TimeMessage: ' + self.text )

    def __str__(self):
        return(self.text )


class EmcyMessage(): # 7.2.7.2 Emergency object services
    '''
    data: data bytes    
    '''
    def __init__( self, dlc: int, data : bytes ):     
        if dlc == 8: 
            self.eec, self.er = unpack_from('<HB', data)            
            self.text = f'EMCY eec:{self.eec:#x}, er:{self.er}'
            if self.eec in EMCY_ERRORS:
                self.text = self.text + ',' + EMCY_ERRORS.get(self.eec)
            else:
                ec = self.eec >> 8
                if ec in EMCY_ERRORCODE_CLASSES:
                    self.text = self.text + ',' + EMCY_ERRORCODE_CLASSES.get(ec)
        else:
            self.text = f'wrong EMCY'


    def __repr__(self):
        return('EmcyMessage: ' + self.text )

    def __str__(self):
        return(self.text )


class ErrCtrlMessage():
    '''
    data: data bytes    
    '''
    def __init__( self, data : bytes ): 
        if data is None:
            self.text = f'Node-Guarding Request (RTR)' 
        elif len(data) == 1:
            s = data[0] & 0x7f
            self.state = { 0 : 'Boot-Up', 4 : 'Stopped', 5: 'Operational', 127 : 'Preoperational'}.get(s, 'unknown')
            self.text = f'Heartbeat: {self.state}'
        else:
            self.text = f'wrong Node-Guarding'

    def __repr__(self):
        return('ErrCtrlMessage: ' + self.text )

    def __str__(self):
        return(self.text )



class SdoMessage():
    '''
    data: data bytes
    client: message sent by client (True) or by data provider = server (False)
    '''
    def __init__( self, data : bytes, client : bool ):  
        self.index = 0
        self.subindex = 0
        cs = (unpack_from( '<B', data )[0] & 0b11100000) >> 5 # command specifier

        if client:
            if cs == 0: # 7.2.4.3.4 Protocol SDO download segment
                cb = data[0]                
                n = (cb & 0b1110) >> 1
                c = bool(cb & 0b01)
                t = 'T' if (cb & 0b010000) else '!T'
                d = self.formatData(data[4:8-n])
                self.text = f'client: download segment request ({t}) = {d} '
                if c: self.text += ' (last segment)'

            elif cs == 1: # 7.2.4.3.3 Protocol SDO download initiate
                cb, self.index, self.subindex = unpack_from( '<BHB', data )
                s = bool(cb & 0b1)
                e = bool((cb & 0b10) >> 1)                
                if e:
                    if s: 
                        n = (cb & 0b1100) >> 2
                        d = self.formatData(data[4:8-n])
                        self.text = f'client: download request = {d}'
                    else:
                        d = self.formatData(data[4:8])                
                        self.text = f'client: download request = {d} (unspecified length)'                                          
                else:
                    if s:
                        numberOfBytes = unpack_from( '<L', data, 4 )[0]
                        self.text = f'client: initiate download request for {numberOfBytes} bytes'
                    else:
                        self.text = 'client: initiate download request'
            elif cs == 2: # 7.2.4.3.6 Protocol SDO upload initiate
                cb, self.index, self.subindex = unpack_from( '<BHB', data )                
                self.text = 'client: initiate upload request'    
            elif cs == 3: # 7.2.4.3.7 Protocol SDO upload segment
                cb = data[0]
                t = 'T' if (cb & 0b010000) else '!T'
                self.text = f'client: upload segment request ({t})'
            elif cs == 4:
                abortCode = unpack_from( '<L', data, 4 )[0]
                message = SDO_ABORT_CODES.get(abortCode, f' abort code:{abortCode:#x}')                 
                self.text = f'client: abort transfer request: "{message}" '
            elif cs == 5: 
                cb = data[0]
                sub = cb & 0b01 # client subcommand                
                if sub == 0: # 7.2.4.3.13 Protocol SDO block upload initiate
                    cb, self.index, self.subindex = unpack_from( '<BHB', data )                        
                    self.text = 'client: initiate block upload request'
                elif sub == 1: # 7.2.4.3.15 Protocol SDO block upload end
                    self.text = 'client: end block upload request'
                elif sub == 2: # 7.2.4.3.14 Protocol SDO block upload sub-block
                    cb, ackseq, blocksize = unpack_from( '<BBB', data )  
                    self.text = f'client: block upload response ackseq:{ackseq}, {blocksize} segments per block'
                elif sub == 3: # 7.2.4.3.13 Protocol SDO block upload initiate
                    cb, self.index, self.subindex = unpack_from( '<BHB', data )                        
                    self.text = 'client: block upload: start upload'
            elif cs == 6: 
                cb = data[0]
                sub = cb & 0b01 # client subcommand
                if cs == 0: # 7.2.4.3.9 Protocol SDO block download initiate
                    cb, self.index, self.subindex, size = unpack_from( '<BHBL', data )          
                    cc = bool( cb & 0b100) # CRC support
                    s = bool(cb & 0b010) 
                    self.text = 'client: block download '
                    if s: self.text += f'size: {size}'
                elif cs == 1: # 7.2.4.3.11 Protocol SDO block download end
                    self.text = 'client: end block download request'
            elif cs == 7:
                self.text = ''      
            elif cs & 0x80: # 7.2.4.3.10 Protocol SDO block download sub-block
                self.text = 'client: block download sub-block'  

        else: # server (data provider)
            if cs == 0: # 7.2.4.3.7 Protocol SDO upload segment
                cb = data[0]         
                n = (cb & 0b1110) >> 1
                c = bool(cb & 0b01)
                t = 'T' if (cb & 0b010000) else '!T'
                d = self.formatData(data[1:8-n])                
                self.text = f'server: upload segment response ({t}) = {d}'
                if c: self.text += ' (last segment)'                
            elif cs == 1: # 7.2.4.3.4 Protocol SDO download segment
                t = 'T' if (cb & 0b010000) else '!T'          
                self.text = f'server: download segment response ({t})'
            elif cs == 2:  # 7.2.4.3.6 Protocol SDO upload initiate
                cb, self.index, self.subindex = unpack_from( '<BHB', data )
                s = bool(cb & 0b1)
                e = bool((cb & 0b10) >> 1)                  
                if e:
                    if s: 
                        n = (cb & 0b1100) >> 2
                        #d = [hex(x) for x in data[4:8-n]]
                        d = self.formatData(data[4:8-n]) 
                        self.text = f'server: upload response = {d}'
                    else:
                        d = self.formatData(data[4:8]) 
                        self.text = f'server: upload response = {d} (unspecified length)' 
                else:               
                    if s:
                        numberOfBytes = unpack_from( '<L', data, 4 )[0]
                        self.text = f'server: initiate upload response length={numberOfBytes} bytes'
                    else:
                        self.text = f'server: initiate upload response'                    
            elif cs == 3:  # 7.2.4.3.3 Protocol SDO download initiate
                cb, self.index, self.subindex = unpack_from( '<BHB', data )        
                self.text = 'server: initiate download response' 

            elif cs == 4:
                abortCode = unpack_from( '<L', data, 4 )[0]                     
                message = SDO_ABORT_CODES.get(abortCode, f' abort code:{abortCode:#x}')                 
                self.text = f'server: abort transfer request: "{message}" '
            elif cs == 5: 
                cb = data[0]
                sub = cb & 0b11 # server subcommand 
                if sub == 0: # 7.2.4.3.9 Protocol SDO block download initiate        
                    cb, self.index, self.subindex, blocksize = unpack_from( '<BHBB', data )          
                    cc = bool( cb & 0b100) # CRC support
                    s = bool(cb & 0b010) 
                    self.text = f'server: block download. {blocksize} segments per block'
                elif sub == 1: # 7.2.4.3.11 Protocol SDO block download end
                    self.text = 'server: end block download response'
                elif sub == 2: # 7.2.4.3.10 Protocol SDO block download sub-block
                    cb, ackseq, blocksize = unpack_from( '<BBB', data )  
                    self.text = f'server: block download response ackseq:{ackseq}, {blocksize} segments per block'
            elif cs == 6:
                cb = data[0]
                sub = cb & 0b01 # client subcommand                
                if sub == 0: # 7.2.4.3.13 Protocol SDO block upload initiate
                    cb, self.index, self.subindex = unpack_from( '<BHB', data )                        
                    self.text = 'server: initiate block upload response'  
                elif sub == 1: # 7.2.4.3.15 Protocol SDO block upload end
                    self.text = 'server: end block upload response'              
            elif cs == 7:
                self.text = '' 
            elif cs & 0x80: # 7.2.4.3.14 Protocol SDO block upload sub-block
                self.text = 'server: block upload sub-block'              

    def formatData(self, data : bytes ):
        s = str(data).removeprefix("b'")
        s = s.removesuffix("'")
        result = '['
        for i, d in enumerate( data):
            if i != 0 : result += ' '
            result = result + format(d, '#04x')
        result = result + '] = [' + s + ']'
        return result

    def __repr__(self):
        return('SdoMessage: ' + self.text + f' - Object: {self.index:#x}/{self.subindex:x}')

    def __str__(self):
        return(self.text + f' - Object: {self.index:#x}/{self.subindex:x}')




class CanOpenMessage:
    def __init__(self, number : int, millis : int, id : int, dlc : int, data : bytes ):
        self.canOpenObject = CANopenType.NONE
        self.number = number
        self.node = id & 0b1111111
        self.index = 0
        self.subindex = 0   
        self.canOpenObject = CANopenType( (id & 0b11110000000) >> 7 )

        if self.canOpenObject == CANopenType.NMT:
            nmt = NmtMessage(data)
            self.text = str(nmt)
        elif self.canOpenObject == CANopenType.EMCY and self.node == 0:
            self.text = f'SYNC'
        elif self.canOpenObject == CANopenType.EMCY:         
            self.text = EmcyMessage(dlc, data)
        elif self.canOpenObject == CANopenType.TIME and self.node == 0:
            self.text = str(TimeMessage(data))
        elif self.canOpenObject == CANopenType.PDO1_T:
            self.text = f'Transmit PDO1'
        elif self.canOpenObject == CANopenType.PDO1_R:
            self.text = f'Receive PDO1'
        elif self.canOpenObject == CANopenType.PDO2_T:
            self.text = f'Transmit PDO2'
        elif self.canOpenObject == CANopenType.PDO2_R:
            self.text = f'Receive PDO2'
        elif self.canOpenObject == CANopenType.PDO3_T:
            self.text = f'Transmit PDO3'
        elif self.canOpenObject == CANopenType.PDO3_R:
            self.text = f'Receive PDO3'
        elif self.canOpenObject == CANopenType.PDO4_T:
            self.text = f'Transmit PDO4'
        elif self.canOpenObject == CANopenType.PDO4_R:
            self.text = f'Receive PDO4'
        elif self.canOpenObject == CANopenType.SDO_R and dlc == 8:
            sdo = SdoMessage( data, True)
            self.text = sdo.text
            self.index = sdo.index
            self.subindex = sdo.subindex
        elif self.canOpenObject == CANopenType.SDO_T and dlc == 8:
            sdo = SdoMessage( data, False)
            self.text = sdo.text
            self.index = sdo.index
            self.subindex = sdo.subindex
        elif self.canOpenObject == CANopenType.ERR_CTRL and dlc == 1:
            self.text = str(ErrCtrlMessage(data))
        else:
            self.canOpenObject = CANopenType.NONE
            self.text = '' # no CanOpen Message
        
 
    def __repr__(self):
        return('CanMessage: ' + self.text)
    
    def __str__(self):
        return(self.text)
    


